import json
import sys
import argparse
import uproot
import difflib
import logging
from pathlib import Path
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.dataset_tools import rucio_utils, preprocess, max_files, max_chunks
from coffea.dataset_tools.dataset_query import print_dataset_query, DataDiscoveryCLI
from rich.console import Console
from rich.table import Table
from dask.diagnostics import ProgressBar
from dask.distributed import Client

NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def generate_json(config, is_data):
    data = {}

    print("Creating json file...")
    for dataset_name, metadata in config.items():
        print("Preparing", dataset_name)

        # If it's data, limit the metadata fields
        if is_data:
            metadata = {
                "mc_campaign": metadata["mc_campaign"],
                "process": metadata["process"],
                "dataset": metadata["dataset"],
            }
        else:
            metadata = {
                "mc_campaign": metadata["mc_campaign"],
                "process": metadata["process"],
                "dataset": metadata["dataset"],
                "xsec": metadata["xsec"],
                "genEventSumw": 0.0,
            }

        data[dataset_name] = metadata

    print(f"\nQuerying replica sites")
    ddc = DataDiscoveryCLI()
    ddc.do_allowlist_sites(["T1_US_FNAL_Disk", "T2_US_Wisconsin", "T2_CH_CERN", "T2_FI_HIP", "T2_UK_London_IC"])
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="round-robin")

    dataset_runnable, dataset_updated = preprocess_json(dataset)

    if not is_data:
        for dataset_name, data in dataset_runnable.items():
            print(f"\nCalculcating genEventSumw for {dataset_name}")
            file_paths = list(data['files'].keys())

            for file_path in file_paths:
                genEventSumw = get_genevents_from_coffea(file_path)
                data["metadata"]["genEventSumw"] += genEventSumw

    return dataset_runnable, dataset_updated

def get_genevents_from_coffea(rootFile):
    filepath = f"{rootFile}"
    try:
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"},
                schemaclass=NanoAODSchema
        ).events()

        genEventSumw = int(events.genEventSumw.compute()[0])
        print("genEventSumw", genEventSumw)
        return genEventSumw

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0, 0.0, 0.0

def save_json(output_file, data, data_all):
    """
    Save the processed JSON data to a file. If data and data_all are different,
    throw an error and output the differences. If they are the same, save only data.
    """
    output_path = Path(output_file)

    # Compare the contents of data and data_all
    if data != data_all:
        # Convert the data to JSON strings for comparison
        data_str = json.dumps(data, indent=4, sort_keys=True)
        data_all_str = json.dumps(data_all, indent=4, sort_keys=True)

        # Generate a human-readable difference using difflib
        diff = difflib.unified_diff(
            data_str.splitlines(), data_all_str.splitlines(),
            fromfile='data', tofile='data_all', lineterm=''
        )

        # Join and format the diff output
        diff_output = '\n'.join(diff)

        logging.error("Error: The contents of 'data' and 'data_all' are different. Differences:")
        logging.error(f"\n{diff_output}")

        raise ValueError("Aborting save due to differences between 'data' and 'data_all'.")

    # Check if the file already exists and warn if it will be overwritten
    if output_path.exists():
        logging.warning(f"{output_file} already exists, overwriting.")

    # Save the processed data to the output file
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)
    logging.info(f"JSON data successfully saved to {output_file}")

def preprocess_json(fileset):
    chunks = 100_000

    print("\nPreprocessing files")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=max_files(fileset),
            step_size=chunks,
            skip_bad_files=False,
            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
        )

    print("Preprocessing completed.\n")

    return dataset_runnable, dataset_updated

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON configuration file")
    parser.add_argument("output_file", type=str, help="Path to the output JSON configuration file")

    # Parse the arguments
    args = parser.parse_args()

    # Create the Dask client
    client = Client(n_workers=4, threads_per_worker=1, memory_limit='2GB')

    # Load the configuration file
    config = load_config(args.input_file)

    # Determine if the input is 'data' based on the file name
    is_data = 'data' in args.input_file

    # Generate the JSON datasets
    dataset_runnable, dataset_updated = generate_json(config, is_data)

    # Save the datasets to JSON
    save_json(args.output_file,  dataset_runnable, dataset_updated)

