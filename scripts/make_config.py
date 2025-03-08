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

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.dataset_tools import rucio_utils, preprocess, max_files, max_chunks
from coffea.dataset_tools.dataset_query import print_dataset_query, DataDiscoveryCLI
from rich.console import Console
from rich.table import Table
from dask.diagnostics import ProgressBar
from dask.distributed import Client

NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

#warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")
#warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def filter_by_process(data, process_name):
    """
    Filters the dictionary to return only entries where the "process" matches the given process_name.

    :param data: The dictionary containing dataset information
    :param process_name: The process name to filter by
    :return: A dictionary with filtered entries
    """
    return {key: value for key, value in data.items() if value.get("process") == process_name}

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def query_datasets(data, run):

    for key, value in data.items():
        process = value.get('process')

    print(f"\nQuerying replica sites")
    ddc = DataDiscoveryCLI()

    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="choose")

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

        genEventSumw = events.genEventSumw.compute()[0]
        print(genEventSumw)
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
    parser.add_argument("dataset", type=str, help="Dataset process to filter")  # New argument

    # Parse the arguments
    args = parser.parse_args()

    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run[:4]}/{args.run}/{args.run}_bkg_cfg.json"

    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run[:4]}/{args.run}/{args.run}_bkg_cfg.json"

    # Create the Dask client
    client = Client(n_workers=4, threads_per_worker=1, memory_limit='2GB', nanny=False)

    try:
        # Load the configuration file
        config = load_config(input_file)

        # Filter configuration based on process name
        filtered_config = filter_by_process(config, args.dataset)

        # Query datasets
        dataset = query_datasets(filtered_config, args.run)

        # Compute sumw values
        sumw_dataset = get_sumw(dataset)

        # Update original config with sumw values
        for key, value in sumw_dataset.items():
            if key in config:
                config[key]["genEventSumw"] = value.get("genEventSumw", 0.0)

        # Save the updated configuration
        save_json(output_file, config)

    finally:
        # Ensure the Dask client is properly closed
        client.close()
