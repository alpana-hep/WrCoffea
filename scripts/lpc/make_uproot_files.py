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
import uproot
import ROOT
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
                            if key not in mwr_mn_files:
#                                print(mwr_mn_files[key])
                                mwr_mn_files[key] = {
                                    "files": {},
                                    "metadata": {
                                        "mc_campaign": metadata["mc_campaign"],
                                        "process": metadata["process"],
                                        "dataset": metadata["dataset"],
                                        "xsec": metadata["xsec"]
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

    total_files = len(mwr_mn_files)  # Total number of iterations
    for index, (mass_point, cfg) in enumerate(mwr_mn_files.items(), start=1):
        output_file_name = f"{run}NanoAODv7_{mass_point}_TuneCP5-madgraph-pythia8.root"
        
        print(f"Processing mass point {index}/{total_files}: {mass_point}")
        start_time = time.time()  # Start the timer
        
        filter_and_merge_single_dictionary(cfg, output_file_name, mass_point)
        
        end_time = time.time()  # End the timer
        elapsed_time = end_time - start_time
        print(f"Time taken for {mass_point}: {elapsed_time:.2f} seconds\n")

    return mwr_mn_files

def filter_and_merge_single_dictionary(input_dict, output_file_name, point):
    """
    Filters events from ROOT files based on a specified branch and appends the filtered events to a single output ROOT file.

    Parameters:
    - input_dict: Dictionary containing file paths and metadata.
    - output_file_name: Name of the output ROOT file to append filtered events.
    """
    # Open or create the output ROOT file
    output_file_mode = "UPDATE" if os.path.exists(output_file_name) else "RECREATE"
    output_file = ROOT.TFile(output_file_name, output_file_mode)
    output_tree = None

    files = input_dict['files']
    metadata = input_dict.get('metadata', {})

    print(f"Processing metadata: {metadata}")
    for file_path, tree_name in files.items():
        print(f"Processing file: {file_path}")

        # Open the input ROOT file
        input_file = ROOT.TFile.Open(file_path)
        if not input_file or input_file.IsZombie():
            print(f"Error opening file: {file_path}")
            continue

        # Get the tree from the file
        input_tree = input_file.Get(tree_name)
        if not input_tree:
            print(f"Tree '{tree_name}' not found in file: {file_path}")
            continue

        # Check if the branch exists in the tree
        # Split the input string into parts
        base, rest = point.split("_WR")
        mw, mn = rest.split("_N")

        branch_name = f"GenModel_{base}_MWR{mw}_MN{mn}_TuneCP5_13TeV_madgraph_pythia8"

        if not input_tree.GetBranch(branch_name):
            print(f"Branch '{branch_name}' not found in tree '{tree_name}' of file: {file_path}")
            continue

        # Create a new tree structure in the output file on first pass
        if output_tree is None:
            output_file.cd()
            output_tree = input_tree.CloneTree(0)  # Clone structure but no entries

        for event in input_tree:
            # Ensure the branch exists and explicitly equals 1
            if hasattr(event, branch_name) and getattr(event, branch_name) == 1:
                output_tree.Fill()

        input_file.Close()

    # Write the combined filtered tree to the output file
    if output_tree and output_tree.GetEntries() > 0:
        output_file.cd()  # Ensure the output file is the current directory
        output_tree.Write("", ROOT.TObject.kOverwrite)  # Write the tree to the file
        print(f"Filtered events written to {output_file_name}")
    else:
        print("No events passed the filter criteria.")

    output_file.Close()

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)

    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("run", type=str, choices=["Run2Autumn18", "Run2Summer20UL18", "Run3Summer22"], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("sample", type=str, choices=["bkg", "sig", "data"], help="Sample type (bkg, sig, data)")

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
#    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run}/{args.run}_{args.sample}_cfg.json"
    input_file = "filtered_ordered.json" 
#    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{args.run}/{args.run}_{args.sample}_preprocessed.json"

    # Load the configuration file
    mwr_mn_files = load_config(input_file)

    total_files = len(mwr_mn_files)  # Total number of iterations
    for index, (mass_point, cfg) in enumerate(mwr_mn_files.items(), start=1):
        output_file_name = f"{args.run}NanoAODv7_{mass_point}_TuneCP5-madgraph-pythia8.root"

        print(f"Processing mass point {index}/{total_files}: {mass_point}")
        start_time = time.time()  # Start the timer

        filter_and_merge_single_dictionary(cfg, output_file_name, mass_point)

        end_time = time.time()  # End the timer
        elapsed_time = end_time - start_time
        print(f"Time taken for {mass_point}: {elapsed_time:.2f} seconds\n")

 #   return mwr_mn_files

#    dataset = get_signal_files(config, args.run)


