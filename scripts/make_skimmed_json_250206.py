import json
import argparse
import subprocess
import uproot
import logging
from coffea.dataset_tools import preprocess
from dask.diagnostics import ProgressBar
from pathlib import Path
import difflib
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def filter_by_process(data, process_name):
    return {key: value for key, value in data.items() if value.get("process") == process_name}

def replace_files_in_json(data, run, year, era, umn):
    """
    Clears 'files' and 'form' entries from the provided JSON data and fetches new file paths.
    """

    # Keys to move into "metadata"
#    metadata_keys = ["das_name", "run", "year", "era", "dataset", "physics_group", "xsec", "datatype"]

    metadata_keys = ["das_name", "run", "year", "era", "dataset", "physics_group", "datatype"]
    # Transform JSON while keeping "metadata" below "files"
    for key in data:
        entry = data[key]
        metadata = {k: entry.pop(k) for k in metadata_keys if k in entry}
    
        # Ensure "files" exists
        files = entry.pop("files", {})

        # Reconstruct the dictionary with "files" first and "metadata" after
        data[key] = {
            "files": files,
            "metadata": metadata
        }

    for dataset_name, dataset_info in data.items():

        # Get the dataset name from metadata
        dataset = dataset_info["metadata"]["dataset"]

        if umn:
            root_files = get_root_files_from_umn(dataset, era)
        else:
            root_files = get_root_files_from_eos(dataset, run, year, era)

        if root_files:
            for file_path in root_files:
                dataset_info["files"][file_path] = "Events"
        else:
            logging.warning(f"No ROOT files found for dataset {dataset_name}")

    return data

def get_root_files_from_umn(dataset, mc_campaign):
#    base_path = f"/uscms/home/bjackson/nobackup/WrCoffea/test/{dataset}/"
    base_path = f"/local/cms/user/jack1851/skims/{mc_campaign}/{dataset}/"
    root_files = []

    # Walk through the directory and collect .root files
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".root"):
                    root_files.append(os.path.join(root, file))
        logging.info(f"Found {len(root_files)} ROOT files for dataset {dataset}")
    else:
        print(f"Error: Base path '{base_path}' does not exist.")

    return root_files

def get_root_files_from_eos(dataset, run, year, era):
    """
    Use xrdfs to get the list of ROOT files from EOS for a given dataset.
    """
    base_path = f"/store/user/wijackso/WRAnalyzer/skims/2025/{run}/{year}/{era}/{dataset}/"
    cmd = ["xrdfs", "root://cmseos.fnal.gov", "ls", base_path]

    try:
        # Execute the xrdfs command to list the files in the directory
        output = subprocess.check_output(cmd, universal_newlines=True)
        # Filter for .root files
        root_files = [f"root://cmseos.fnal.gov/{line.strip()}" for line in output.splitlines() if line.endswith(".root")]
        logging.info(f"Found {len(root_files)} ROOT files for dataset {dataset}")
        return root_files
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list ROOT files for {dataset}: {e}")
        return []

def preprocess_json(fileset, chunks=100_000, timeout=3600):
    """
    Preprocess the JSON file and handle large datasets in chunks.
    """
    print()
    logging.info(f"Starting preprocessing with {chunks} chunks and {timeout}s timeout.")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=fileset,
            step_size=chunks,
            skip_bad_files=False,
        )

    logging.info("Preprocessing completed.")
    print()
    return dataset_runnable, dataset_updated

def save_json(output_file, data, data_all):
    """
    Save the processed JSON data to a file. If data and data_all are different,
    throw an error and output the differences. If they are the same, save only data.
    """
    output_path = Path(output_file)

    # Ensure the directories for the output file exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

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

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("era", type=str, choices=["Run2Autumn18", "RunIISummer20UL18", "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix",], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("--umn", action="store_true", help="Enable UMN mode (default: False)")
    parser.add_argument("--chunks", type=int, default=100_000, help="Chunk size for processing")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout for uproot file handling")

    # Parse the arguments
    args = parser.parse_args()

    era_mapping = {
        "RunIISummer20UL18": {"run": "RunII", "year": "2018"},
        "Run3Summer22": {"run": "Run3", "year": "2022"},
    }
    mapping = era_mapping.get(args.era)
    if mapping is None:
        raise ValueError(f"Unsupported era: {args.era}")
    run, year = mapping["run"], mapping["year"]


    input_file = f"data/configs/{run}/{year}/{args.era}_data.json"
    output_file = f"data/jsons/{run}/{year}/{args.era}/{args.era}_data_preprocessed_skims.json"

    # Load the input JSON file
    try:
        with open(input_file, 'r') as file:
            fileset = json.load(file)
        logging.info(f"Loaded input JSON file from {input_file}")
    except FileNotFoundError:
        logging.error(f"Input file {input_file} not found!")
        exit(1)

#    fileset = filter_by_process(fileset, args.sample)

    # Clear the "files" content and update with new ROOT files
    fileset = replace_files_in_json(fileset, run, year, args.era, args.umn)

    # Preprocess the updated fileset
    dataset_runnable, dataset_updated = preprocess_json(fileset, chunks=args.chunks, timeout=args.timeout)

    # Save the modified JSON to the output file
    save_json(output_file, dataset_runnable, dataset_updated)
