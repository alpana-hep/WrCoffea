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
#        ddc.do_allowlist_sites(["T2_US_Wisconsin", "T2_US_Caltech", "T2_US_Vanderbilt", "T2_US_UCSD", "T2_US_Nebraska", "T2_US_Florida", "T2_UK_London_IC"]) #Remove T2_US_Nebraska
        ddc.do_allowlist_sites(["T2_US_Wisconsin", "T2_CH_CERN", "T2_UK_London_IC", "T2_US_UCSD", "T2_US_FLORIDA"]) #"T2_FI_HIP"
    elif run == "Run3Summer22":
        ddc.do_allowlist_sites(["T2_US_Wisconsin", "T2_US_Caltech", "T2_US_Vanderbilt", "T2_US_UCSD", "T2_US_Nebraska", "T2_US_Florida", "T2_UK_London_IC"]) #Remove T2_US_Nebraska
    elif run == "Run3Summer23":
        ddc.do_blocklist_sites(["T2_US_MIT", "T2_PL_Cyfronet"]) # Gave error
    elif run == "Run3Summer23BPix": # GOOD
        ddc.do_blocklist_sites(["T2_US_MIT"]) # Gave error
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="first")
    return dataset

def get_sumw(dataset_runnable):
    for dataset_name, data in dataset_runnable.items():
        print(f"Calculcating genEventSumw for {dataset_name}")
        file_paths = list(data['files'].keys())

        for file_path in file_paths:
            genEventSumw = get_genevents_from_coffea(file_path)
            data["metadata"]["genEventSumw"] += genEventSumw

        del data['files']
    print()
    return dataset_runnable

def get_genevents_from_coffea(rootFile):
    filepath = f"{rootFile}"
    try:
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"},
                schemaclass=NanoAODSchema
        ).events()

        genEventSumw = int(events.genEventSumw.compute()[0])
        return genEventSumw

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0, 0.0, 0.0

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
