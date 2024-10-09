from coffea.dataset_tools import preprocess, max_chunks, max_files
import json
#import gzip
import argparse
from dask.diagnostics import ProgressBar
import os
import sys
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
#import warnings

# This script should go into the skimmed files directory on EOS, and make a preprocessed json file from them.

NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False
#warnings.filterwarnings("error", module="coffea.*")

def load_json(filename):
    json_file_path = f'{filename}'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def get_files_from_directory(directory):
    # Get all files in the directory
    files = {}
    if os.path.exists(directory):
        for file in os.listdir(directory):
            if file.endswith(".root"):  # Only include .root files
                file_path = os.path.join(directory, file)
                files[file_path] = "Events"
    else:
        print(f"Directory {directory} does not exist.")
    return files

def get_genevents_from_coffea(filepath):
    try:
       # Open the ROOT file using NanoEventsFactory
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"},
                schemaclass=NanoAODSchema
        ).events()

        # Calculate the genEventCount, genEventSumw, and genEventSumw2
        genEventCount = int(events.genEventCount.compute()[0])
        genEventSumw = int(events.genEventSumw.compute()[0])
        genEventSumw2 = int(events.genEventSumw2.compute()[0])
        return genEventCount, genEventSumw, genEventSumw2

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0, 0.0, 0.0

def replace_root_files_with_skims(data, base_dir):
    # Get the dataset name from the metadata
    dataset = data['metadata']['dataset']

    # Define the skims directory based on the dataset
    skims_dir = os.path.join(base_dir, dataset)

    # Check if the directory exists
    if not os.path.exists(skims_dir):
        raise FileNotFoundError(f"Directory {skims_dir} does not exist")

    # Create a new dictionary for the skims
    skims_dict = {}

    # List all .root files in the skims directory
    skim_files = [f for f in os.listdir(skims_dir) if f.endswith('.root')]

    # Number of files to match
    num_skim_files = len(skim_files)

    # Loop through the root files and only match the number of available skim files
    for i, (root_file, events) in enumerate(data['files'].items()):
        if i < num_skim_files:
            # Replace the root file with the corresponding skim file
            skim_file_path = os.path.join(skims_dir, skim_files[i])
            skims_dict[skim_file_path] = events
        else:
            # Stop adding files when all skims are used
            break

    # Replace the original 'files' dictionary with the new skims dictionary
    data['files'] = skims_dict

    return data

def generate_json(config):
    data = {}

    for dataset_name, filepaths in config.items():
        # Base path for each dataset
        # Directory where the files are located
        base_skim_directory = f'skims/{filepaths["metadata"]["dataset"]}' # Assuming the directory is named exactly as the dataset

        # Get all root files from the directory
        skimmed_files = get_files_from_directory(base_skim_directory)

        print(skimmed_files)
        if not skimmed_files:
            print(f"No files found for {dataset_name}. Skipping.")
            continue

        directory = "skims/"
        updated_data = replace_root_files_with_skims(filepaths, directory)

        # Add this dataset's information to the data dictionary
        data[dataset_name] = updated_data

    return data

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    print(f"Preprocessing...")
    config = load_config("jsons/DY_to_skim.json")

    fileset = generate_json(config)

    chunks = 100_000

    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=fileset,
            step_size=chunks,
            skip_bad_files=False,
        )

    print("Preprocessing completed. Comparing dataset_runnable and dataset_updated...\n")

    with open(f"jsons/DY_skimmed_preprocessed.json", "w") as file:
        print(f"Saved preprocessed fileset to jsons/DY_skimmed_preprocessed.json")
        json.dump(dataset_runnable, file, indent=2)

    with open(f"jsons/DY_skimmed_all.json", "w") as file:
        print(f"Saved preprocessed fileset to jsons/DY_skimmed_all.json")
        json.dump(dataset_updated, file, indent=2)
~                                                      
