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
from rich.console import Console
from rich.table import Table
from dask.diagnostics import ProgressBar
import os
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

def get_metadata(config, is_data, is_signal):
    data = {}

    print("Creating json file...")
    for dataset_name, metadata in config.items():

        # If it's data, limit the metadata fields
        if is_data:
            metadata = {
                "mc_campaign": metadata["mc_campaign"],
                "process": metadata["process"],
                "dataset": metadata["dataset"],
            }
        elif is_signal:
            metadata = {
                "mc_campaign": metadata["mc_campaign"],
                "process": metadata["process"],
                "dataset": metadata["dataset"],
                "xsec": metadata["xsec"],
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

    return data

def query_datasets(data, run):
    print(f"\nQuerying replica sites")
    ddc = DataDiscoveryCLI()
    if run == "Run2Summer20UL18":
#        ddc.do_allowlist_sites(["T2_US_Wisconsin", "T2_US_Caltech", "T2_US_Vanderbilt", "T2_US_UCSD", "T2_US_Nebraska", "T2_US_Florida", "T2_UK_London_IC"]) #Remove T2_US_Nebraska
        ddc.do_allowlist_sites(["T2_US_Wisconsin", "T2_CH_CERN", "T2_UK_London_IC", "T2_US_UCSD", "T2_US_FLORIDA"]) #"T2_FI_HIP"
    if run == "Run3Summer22":
        ddc.do_allowlist_sites(["T2_US_Wisconsin", "T2_US_Caltech", "T2_US_Vanderbilt", "T2_US_UCSD", "T2_US_Nebraska", "T2_US_Florida", "T2_UK_London_IC"]) #Remove T2_US_Nebraska
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="first")
    return dataset

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

#        branch_name = "GenModel_WRtoNLtoLLJJ_MWR3200_MN600_TuneCP5_13TeV_madgraph_pythia8"
        if not input_tree.GetBranch(branch_name):
            print(f"Branch '{branch_name}' not found in tree '{tree_name}' of file: {file_path}")
            continue

        # Create a new tree structure in the output file on first pass
        if output_tree is None:
            output_file.cd()
            output_tree = input_tree.CloneTree(0)  # Clone structure but no entries

        # Loop over the events and filter based on the branch
        for event in input_tree:
            if getattr(event, branch_name, False):
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

def preprocess_json(fileset):
    chunks = 100_000

    print("\nPreprocessing files")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=max_files(fileset),
            step_size=chunks,
            skip_bad_files=False,
            uproot_options={"handler": uproot.XRootDSource, "timeout": 60}
#            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
        )

    print("Preprocessing completed.\n")

    return dataset_runnable, dataset_updated

def get_sumw(dataset_runnable):
    for dataset_name, data in dataset_runnable.items():
        print(f"Calculcating genEventSumw for {dataset_name}")
        file_paths = list(data['files'].keys())

        for file_path in file_paths:
            genEventSumw = get_genevents_from_coffea(file_path)
            data["metadata"]["genEventSumw"] += genEventSumw
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
    parser.add_argument("run", type=str, choices=["Run2Autumn18", "Run2Summer20UL18", "Run3Summer22"], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("sample", type=str, choices=["bkg", "sig", "data"], help="Sample type (bkg, sig, data)")

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{args.run}/{args.run}_{args.sample}_cfg.json"
    output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{args.run}/{args.run}_{args.sample}_preprocessed.json"

    # Create the Dask client
#    client = Client(n_workers=4, threads_per_worker=1, memory_limit='2GB', nanny=False)

    # Load the configuration file
    config = load_config(input_file)

    # Determine if the input is 'data' based on the file name
    is_mc = 'bkg' in args.sample
    is_data = 'data' in args.sample
    is_signal = 'sig' in args.sample

#    updated_config = get_metadata(config, is_data, is_signal)

    if not is_signal:
        dataset = query_datasets(config, args.run) #Updated config
    else:
        dataset = get_signal_files(config, args.run)

#    dataset_runnable, dataset_updated = preprocess_json(dataset)

#    compare_preprocessed(dataset_runnable, dataset_updated)

#    if is_mc:
#       dataset_runnable = get_sumw(dataset_runnable)

    # Save the datasets to JSON
#    save_json(output_file, dataset_runnable)

