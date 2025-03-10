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
import multiprocessing
from pathlib import Path
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from dask.diagnostics import ProgressBar
import os
import time
NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def filter_and_merge_single_dictionary(input_dict, output_file_name, point):
    """
    Filters events from ROOT files based on a specified branch and appends the filtered events to a single output ROOT file.

    Parameters:
    - input_dict: Dictionary containing file paths and metadata.
    - output_file_name: Name of the output ROOT file to append filtered events.
    """
    files = input_dict['files']
    metadata = input_dict.get('metadata', {})

    print(f"Processing metadata: {metadata}")

    # Define the branch name based on the `point` parameter
    base, rest = point.split("_WR")
    mw, mn = rest.split("_N")
    condition_branch_name = f"GenModel_{base}_MWR{mw}_MN{mn}_TuneCP5_13TeV_madgraph_pythia8"

    # Initialize an empty dictionary to store arrays for the output file
    output_data = {}

    # Define uproot options for XRootD access
    uproot_options = {"xrootd_handler": uproot.source.xrootd.XRootDSource, "timeout": 60}

    for file_path, tree_name in files.items():
        print(f"Processing file: {file_path}")

        try:
            with uproot.open(file_path, **uproot_options) as file:
                if tree_name not in file:
                    print(f"Tree '{tree_name}' not found in file: {file_path}")
                    continue

                tree = file[tree_name]

                # Check if the branch exists in the tree
                if condition_branch_name not in tree.keys():
                    print(f"Branch '{condition_branch_name}' not found in tree '{tree_name}' of file: {file_path}")
                    continue

                # Process data in chunks
                for chunk in tree.iterate(filter_name="*", library="np", step_size="10 MB"):
                    condition_data = chunk[condition_branch_name]

                    # Filter events where the condition branch value is True
                    mask = condition_data.astype(bool)

                    # Apply the mask to all branches in the chunk
                    for key in chunk:
                        if key not in output_data:
                            output_data[key] = chunk[key][mask]
                        else:
                            output_data[key] = np.concatenate((output_data[key], chunk[key][mask]))
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    # Write the filtered data to the output file
    if output_data:
        with uproot.recreate(output_file_name) as output_file:  # No mode argument
            output_file[tree_name] = output_data
        print(f"Filtered events written to {output_file_name}")
    else:
        print("No events passed the filter criteria.")

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("run", type=str, choices=["Run2Autumn18", "Run2Summer20UL18", "Run3Summer22"], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("sample", type=str, choices=["bkg", "sig", "data"], help="Sample type (bkg, sig, data)")
    parser.add_argument("--start", type=int, default=1, help="Start the loop at a given index (1-based)")

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/scripts/lpc/{args.run}_{args.sample}.json"
#    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{args.run}/{args.run}_{args.sample}.json"

    # Load the configuration file
    mwr_mn_files = load_config(input_file)

    # Get the total number of iterations
    total_files = len(mwr_mn_files)

    # Adjust the loop to start at the given index
    start_index = args.start - 1  # Convert 1-based to 0-based index
    if start_index < 0 or start_index >= total_files:
        print(f"Error: Start index {args.start} is out of range (1 to {total_files}).")
        exit(1)

    # Main processing loop
    for index, (mass_point, cfg) in enumerate(list(mwr_mn_files.items())[start_index:], start=args.start):
        output_dir = f"{args.run}/{mass_point}"
        output_file_name = f"{output_dir}/{args.run}NanoAODv7_{mass_point}_TuneCP5-madgraph-pythia8.root"

        # Make the output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        print(f"Processing mass point {index}/{total_files}: {mass_point}")
        start_time = time.time()  # Start the timer

        filter_and_merge_single_dictionary(cfg, output_file_name, mass_point)

        end_time = time.time()  # End the timer
        elapsed_time = end_time - start_time
        print(f"Time taken for {mass_point}: {elapsed_time:.2f} seconds\n")

