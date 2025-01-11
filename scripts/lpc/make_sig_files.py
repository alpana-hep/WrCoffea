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

def get_signal_files(cfg,run):
    file_contents = ""
    result = subprocess.run(['dasgoclient', '-query', f'file dataset=/WRtoNLtoLLJJ_MWR500to3500_TuneCP5-madgraph-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_rpscan_102X_upgrade2018_realistic_v21-v1/NANOAODSIM'], capture_output=True, text=True)
    file_contents += result.stdout

    prepend_string = 'root://eoscms.cern.ch:1094//eos/cms'
    lines = file_contents.strip().split('\n')
    lines = [f'{prepend_string}{line}' for line in lines]

    pattern = re.compile(r"GenModel_WRtoNLtoLLJJ_MWR(\d+)_MN(\d+)_TuneCP5_13TeV_madgraph_pythia8")
    mwr_mn_files = {}

    for file_name in lines:
        try:
            with uproot.open(file_name) as root_file:
                if "Events" not in root_file:
                    print(f"Failed to get 'Events' tree in file {file_name}")
                    continue
                tree = root_file["Events"]
            for branch_name in tree.keys():
                match = pattern.match(branch_name)
                if match:
                    mwr = match.group(1)
                    mn = match.group(2)
                    key = f"WRtoNLtoLLJJ_WR{mwr}_N{mn}"
                    for dataset_name, metadata in cfg.items():
                        if key == dataset_name:
                            print(key)
                            if key not in mwr_mn_files:
                                mwr_mn_files[key] = {
                                "files": {},
                                "metadata": {
                                    "mc_campaign": metadata["metadata"]["mc_campaign"],
                                    "process": metadata["metadata"]["process"],
                                    "dataset": metadata["metadata"]["dataset"],
                                    "xsec": metadata["metadata"]["xsec"]
                                }
                            }

                            mwr_mn_files[key]["files"][file_name] = "Events"

        except Exception as e:
            print(f"Failed to open file {file_name}: {e}")

#    for mass_point, cfg in mwr_mn_files.items():
#        output_file_name = f"{run}NanoAODv7_{mass_point}_TuneCP5-madgraph-pythia8.root"
#        start_time = time.time()  # Start the timer
#        filter_and_merge_single_dictionary(cfg, output_file_name, mass_point)
#        end_time = time.time()  # End the timer
#        elapsed_time = end_time - start_time
#        print(f"Time taken for {mass_point}: {elapsed_time:.2f} seconds\n")
#        print()

#    total_files = len(mwr_mn_files)  # Total number of iterations
#    for index, (mass_point, cfg) in enumerate(mwr_mn_files.items(), start=1):
#        output_file_name = f"{run}/{mass_point}/{run}NanoAODv7_{mass_point}_TuneCP5-madgraph-pythia8.root"
        
#        print(f"Processing mass point {index}/{total_files}: {mass_point}")
#        start_time = time.time()  # Start the timer
        
#        filter_and_merge_single_dictionary(cfg, output_file_name, mass_point)
        
#        end_time = time.time()  # End the timer
#        elapsed_time = end_time - start_time
#        print(f"Time taken for {mass_point}: {elapsed_time:.2f} seconds\n")

    return mwr_mn_files

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
    branch_name = f"GenModel_{base}_MWR{mw}_MN{mn}_TuneCP5_13TeV_madgraph_pythia8"

    # Initialize an empty dictionary to store arrays for the output file
    output_data = {}

    for file_path, tree_name in files.items():
        print(f"Processing file: {file_path}")

        # Open the input ROOT file and access the tree
        try:
            with uproot.open(file_path) as file:
                if tree_name not in file:
                    print(f"Tree '{tree_name}' not found in file: {file_path}")
                    continue

                tree = file[tree_name]

                # Check if the branch exists in the tree
                if branch_name not in tree.keys():
                    print(f"Branch '{branch_name}' not found in tree '{tree_name}' of file: {file_path}")
                    continue

                # Read the branch as a NumPy array
                branch_data = tree[branch_name].array(library="np")

                # Filter the events where the branch value is True
                mask = branch_data.astype(bool)
                for key, array in tree.arrays(library="np").items():
                    if key not in output_data:
                        output_data[key] = array[mask]
                    else:
                        output_data[key] = np.concatenate((output_data[key], array[mask]))
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            continue

    # Write the filtered data to the output file
    if output_data:
        mode = "update" if os.path.exists(output_file_name) else "recreate"
        with uproot.recreate(output_file_name, mode=mode) as output_file:
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

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run}/{args.run}_{args.sample}_cfg.json"
    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/{args.run}_{args.sample}.json"
#    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{args.run}/{args.run}_{args.sample}.json"

    # Load the configuration file
    config = load_config(input_file)

    dataset = get_signal_files(config, args.run)

    print(dataset)

    # Save the dataset to the output JSON file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure output directory exists
    try:
        with open(output_file, "w") as f:
            json.dump(dataset, f, indent=4)
        print(f"Processed dataset saved to {output_file}")
    except Exception as e:
        print(f"Error: Failed to save JSON to {output_file}: {e}")
