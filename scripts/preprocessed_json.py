import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")

import json
import sys
import argparse
import logging
import warnings
import subprocess
import re
import uproot
import numpy as np
import awkward as ak
import multiprocessing
from pathlib import Path
import os

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.dataset_tools import rucio_utils, preprocess, max_files, max_chunks
from coffea.dataset_tools.dataset_query import print_dataset_query, DataDiscoveryCLI
from rich.console import Console
from rich.table import Table
from dask.diagnostics import ProgressBar
from dask.distributed import Client, progress

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, repo_root)

from python.preprocess_utils import get_era_details, load_json, save_json

NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def filter_json_by_primary_ds_name(json_data, primary_ds_name):
    filtered_data = {
        key: value for key, value in json_data.items()
        if value.get("dataset") == primary_ds_name
    }
    return filtered_data

def filter_by_process(data, process_name):
    return {key: value for key, value in data.items() if value.get("physics_group") == process_name}

def query_datasets(data):
    print(f"\nQuerying replica sites")
    logging.info("Querying replica sites")
    ddc = DataDiscoveryCLI()
    ddc.do_blocklist_sites(["T2_US_MIT"])
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="choose")
    return dataset

def preprocess_json(fileset):
    chunks = 100_000
    logging.info("Preprocessing files")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=max_files(fileset, 2500), #2000 works
            step_size=chunks,
            skip_bad_files=False,
            uproot_options={"handler": uproot.MultithreadedXRootDSource, "timeout": 3600} # or uproot.XRootDSource
        )
    logging.info("Preprocessing completed.")
    return dataset_runnable, dataset_updated

def save_dataset_txt(dataset, output_dir):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for dataset_name, dataset_info in dataset.items():
        metadata = dataset_info.get("metadata", {})
        dataset_filename = metadata.get("dataset", dataset_name)
        sanitized_name = dataset_filename.replace(" ", "_")
        dataset_txt_path = output_dir / f"{sanitized_name}.txt"

        with open(dataset_txt_path, 'w') as txt_file:
            for file_path in dataset_info.get("files", {}):
                txt_file.write(f"{file_path}\n")

        logging.info(f"Saved dataset file list to {dataset_txt_path}")


def main():
    multiprocessing.set_start_method("spawn", force=True)

    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("era", type=str,
                        choices=["RunIISummer20UL16", "RunIISummer20UL17", "RunIISummer20UL18",
                                 "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix"],
                        help="Run era (e.g., RunIISummer20UL18)")
    parser.add_argument("process", type=str, help="Dataset process to filter (e.g. DYJets, TTbar)")
    parser.add_argument('--dataset', type=str, help='Dataset to process (e.g. TTTo2L2Nu')
    args = parser.parse_args()

    run, year, era = get_era_details(args.era)

    if "Muon" in args.process or "EGamma" in args.process:
        input_file = Path("/uscms/home/bjackson/nobackup/WrCoffea/data/configs") / run / year / args.era / f"{args.era}_data.json"
    else:
        input_file = Path("/uscms/home/bjackson/nobackup/WrCoffea/data/configs") / run / year / args.era / f"{args.era}_mc.json"

    output_file = Path("/uscms/home/bjackson/nobackup/WrCoffea/data/jsons") / run / year / args.era / f"{args.era}_{args.process}_preprocessed.json"
    output_txt_dir = Path("/uscms/home/bjackson/nobackup/WrCoffea/data/filepaths") / run / year / args.era

    print()
    logging.info(f"Loading input file {input_file}.")
    config = load_json(str(input_file))
    
    if config is None:
        logging.error("No valid input file found.")
        sys.exit(1)

    client = Client(n_workers=4, threads_per_worker=1, processes=True, memory_limit='2GB', nanny=False)
#    client = Client(n_workers=1, threads_per_worker=1, memory_limit='2GB', nanny=False)
    logging.info("Dask client started.")

    filtered_config = filter_by_process(config, args.process)
    if args.dataset:
        filtered_config = filter_json_by_primary_ds_name(filtered_config, args.dataset)

    dataset = query_datasets(filtered_config)
    print()
    save_dataset_txt(dataset, output_txt_dir)
    print()
    dataset_runnable, dataset_updated = preprocess_json(dataset)
    print()
    save_json(output_file, dataset_runnable, dataset_updated)


if __name__ == "__main__":
    main()
