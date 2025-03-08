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
from dask.distributed import Client, progress
import os
NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_json(file_path):
    """Load JSON data from a file if it exists."""
    file_path = Path(file_path)
    if file_path.exists():
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        logging.error(f"File {file_path} does not exist.")
        return None

def filter_by_process(data, process_name):
    return {key: value for key, value in data.items() if value.get("physics_group") == process_name}

def query_datasets(data):
    print(f"\nQuerying replica sites")
    ddc = DataDiscoveryCLI()
    ddc.do_blocklist_sites(["T2_US_MIT"])
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="choose")
    return dataset

def preprocess_json(fileset):
    chunks = 100_000

    print("\nPreprocessing files")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=max_files(fileset),
            step_size=chunks,
            skip_bad_files=False,
            uproot_options={"handler": uproot.MultithreadedXRootDSource, "timeout": 3600}
#            uproot_options={"handler": uproot.XRootDSource, "timeout": 60}
#            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
        )

    print("Preprocessing completed.\n")

    return dataset_runnable, dataset_updated

def compare_preprocessed(data, data_all):
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

def save_dataset_txt(dataset, output_dir):
    """
    Save each dataset to a separate .txt file where each line contains a file path.
    The filename is derived from the 'dataset' field in metadata.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for dataset_name, dataset_info in dataset.items():
        # Extract dataset name from metadata
        metadata = dataset_info.get("metadata", {})
        dataset_filename = metadata.get("dataset", dataset_name)  # Default to dataset_name if 'dataset' key is missing
        sanitized_name = dataset_filename.replace(" ", "_")  # Ensure a safe filename
        
        dataset_txt_path = output_dir / f"{sanitized_name}.txt"

        with open(dataset_txt_path, 'w') as txt_file:
            for file_path in dataset_info.get("files", {}):  # `files` is a dictionary, get keys (file paths)
                txt_file.write(f"{file_path}\n")

        logging.info(f"Saved dataset file list to {dataset_txt_path}")

def save_json(output_file, data):
    """
    Save the processed JSON data to a file. If the directories for the output file 
    do not exist, create them. If the file already exists, warn about overwriting it.
    """
    output_path = Path(output_file)

    # Create parent directories if they don't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Check if the file already exists and warn if it will be overwritten
    if output_path.exists():
        logging.warning(f"{output_file} already exists, overwriting.")

    # Save the processed data to the output file
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)
    logging.info(f"JSON data successfully saved to {output_file}")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("era", type=str, choices=[
        "Run2Autumn18", 
        "RunIISummer20UL18NanoAODv9", 
        "Run2018A",
        "Run2018B",
        "Run2018C",
        "Run2018D",
        "Run3Summer22", 
        "Run3Summer22EE", 
        "Run3Summer23", 
        "Run3Summer23BPix"
        ], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("dataset", type=str, help="Dataset process to filter (e.g. DYJets, TTbar)")
    args = parser.parse_args()

    era_mapping = {
        "RunIISummer20UL18": {"run": "RunII", "year": "2018"},
        "Run3Summer22": {"run": "Run3", "year": "2022"},
        "Run3Summer22EE": {"run": "Run3", "year": "2022"},
    }
    mapping = era_mapping.get(args.era)
    if mapping is None:
        raise ValueError(f"Unsupported era: {args.era}")
    run, year = mapping["run"], mapping["year"]

    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{run}/{year}/{args.era}.json"
    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{run}/{year}/{args.era}/{args.era}_{args.dataset}_preprocessed.json"
    output_txt_dir = f"/uscms/home/bjackson/nobackup/WrCoffea/data/filepaths/{run}/{year}/{args.era}/"

    logging.info(f"Loading input file {input_file}.")
    config = load_json(input_file)

    if config is None:
        raise FileNotFoundError("No valid input or output file found.")

    # Create the Dask client
    client = Client(n_workers=4, threads_per_worker=1, memory_limit='2GB', nanny=False)

    filtered_config = filter_by_process(config, args.dataset)

    print(filtered_config)

    dataset = query_datasets(filtered_config) #Updated config

    # Save dataset information as text files
    save_dataset_txt(dataset, output_txt_dir)

    dataset_runnable, dataset_updated = preprocess_json(dataset)

    compare_preprocessed(dataset_runnable, dataset_updated)

#    for dataset_name, new_files in dataset_runnable.items():
#        for config_name, metadata in config.items():
#            if dataset_name == config_name:
#                config[config_name] = new_files

    save_json(output_file, dataset_runnable)
