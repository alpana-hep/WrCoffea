import json
import sys
import argparse
import uproot
import difflib
import logging
import warnings
import subprocess
import re
import uproot
import numpy as np
import awkward as ak
import multiprocessing
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

warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def query_datasets(data, run):
    print(f"\nQuerying replica sites")
    ddc = DataDiscoveryCLI()
    if run == "Run2Summer20UL18":
        ddc.do_blocklist_sites(["T2_US_MIT", "T1_US_FNAL_Disk"]) # Gave error
    elif run == "Run3Summer22":
        ddc.do_blocklist_sites(["T2_PL_Cyfronet", "T2_US_Vanderbilt", "T2_TW_NCHC"]) # Gave error
    elif run == "Run3Summer22EE":
        ddc.do_blocklist_sites(["T2_US_MIT", "T2_PL_Cyfronet", "T1_US_FNAL_Disk", "T1_DE_KIT_Disk", "T2_US_Vanderbilt", "T2_TW_NCHC"])
    elif run == "Run3Summer23":
        ddc.do_blocklist_sites(["T2_US_MIT", "T2_PL_Cyfronet", "T2_TW_NCHC"]) # Gave error
    elif run == "Run3Summer23BPix": # GOOD
        ddc.do_blocklist_sites(["T2_US_MIT", "T1_DE_KIT_Disk", "T2_US_Purdue", "T2_PL_Cyfronet", "T2_TW_NCHC"]) # Gave error
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="first")

    return dataset

def get_sumw(dataset_runnable):
    for dataset_name, data in dataset_runnable.items():
        print(f"Calculcating genEventSumw for {dataset_name}")
        file_paths = list(data['files'].keys())

        for file_path in file_paths:
            genEventSumw = get_genevents_from_coffea(file_path)
            data["metadata"]["genEventSumw"] += genEventSumw

        # Remove 'files' key from the dictionary
        del data['files']

        # This gets rid of the parent 'metadata' that comes from DataDiscoveryCLI()
        dataset_runnable[dataset_name] = data['metadata']
    print()
    return dataset_runnable

def get_genevents_from_coffea(rootFile):
    filepath = f"{rootFile}"
    try:
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"},
                schemaclass=NanoAODSchema
        ).events()

        # Check if 'genEventSumw' exists in the file
        if not hasattr(events, "genEventSumw"):
            print(f"File {filepath} does not contain 'genEventSumw'. Skipping...", file=sys.stderr)
            return 0  # Return 0 so that it doesn't affect the sum

        genEventSumw = int(events.genEventSumw.compute()[0])
        return genEventSumw

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0  # Return 0 on error

def save_json(output_file, data):
    """
    Save the processed JSON data to a file. If data and data_all are different,
    throw an error and output the differences. If they are the same, save only data.
    """
    output_path = Path(output_file)

    # Check if the file already exists and warn if it will be overwritten
    if output_path.exists():
        logging.warning(f"{output_file} already exists, overwriting.")

    # Save the processed data to the output file
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)
    logging.info(f"JSON data successfully saved to {output_file}")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("run", type=str, choices=["Run2Summer20UL18", "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix"], help="MC Campaign")
    parser.add_argument("sample", type=str, choices=["bkg"], help="Sample type (bkg, sig, data)")

    # Parse the arguments
    args = parser.parse_args()

    if args.run == "Run2Summer20UL18":
        input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run}/{args.run}_{args.sample}_genxsec_template.json"
    else:
        # Build input and output file paths based on the arguments
        input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run}/{args.run}_{args.sample}_template.json"
    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run}/{args.run}_{args.sample}_cfg.json"

    # Create the Dask client
    client = Client(n_workers=4, threads_per_worker=1, memory_limit='2GB', nanny=False)

    # Load the configuration file
    config = load_config(input_file)

    dataset = query_datasets(config, args.run)

    sumw_dataset = get_sumw(dataset)

    # Save the datasets to JSON
    save_json(output_file, sumw_dataset)
