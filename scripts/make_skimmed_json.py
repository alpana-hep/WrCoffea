import json
import argparse
import subprocess
import uproot
import logging
from coffea.dataset_tools import preprocess
from dask.diagnostics import ProgressBar
from pathlib import Path
import difflib
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def replace_files_in_json(data, run, umn):
    """
    Clears 'files' and 'form' entries from the provided JSON data and fetches new file paths.
    """
    for dataset_name, dataset_info in data.items():
        dataset_info["files"] = {}

        # Get the dataset name from metadata
        dataset = dataset_info["metadata"].get("dataset", "")

        if umn:
            root_files = get_root_files_from_umn(dataset, run)
        else:
            root_files = get_root_files_from_eos(dataset, run)

        if root_files:
            for file_path in root_files:
                dataset_info["files"][file_path] = "Events"
        else:
            logging.warning(f"No ROOT files found for dataset {dataset_name}")

    return data

def get_root_files_from_umn(dataset, mc_campaign):
    base_path = f"/uscms/home/bjackson/nobackup/WrCoffea/skims/{mc_campaign}/{dataset}/"
    root_files = []

    # Walk through the directory and collect .root files
    if os.path.exists(base_path):
        for root, _, files in os.walk(base_path):
            for file in files:
                if file.endswith(".root"):
                    root_files.append(os.path.join(root, file))
        logging.info(f"Found {len(root_files)} ROOT files for dataset {dataset}")
    else:
        print(f"Error: Base path '{base_path}' does not exist.")

    return root_files

def get_root_files_from_eos(dataset, mc_campaign):
    """
    Use xrdfs to get the list of ROOT files from EOS for a given dataset.
    """
    base_path = f"/store/user/wijackso/WRAnalyzer/Skim_Tree_Lepton_Pt45/{mc_campaign}/{dataset}/"
    cmd = ["xrdfs", "root://cmseos.fnal.gov", "ls", base_path]

    try:
        # Execute the xrdfs command to list the files in the directory
        output = subprocess.check_output(cmd, universal_newlines=True)
        # Filter for .root files
        root_files = [f"root://cmseos.fnal.gov/{line.strip()}" for line in output.splitlines() if line.endswith(".root")]
        logging.info(f"Found {len(root_files)} ROOT files for dataset {dataset}")
        return root_files
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list ROOT files for {dataset}: {e}")
        return []

def preprocess_json(fileset, chunks=100_000, timeout=3600):
    """
    Preprocess the JSON file and handle large datasets in chunks.
    """
    print()
    logging.info(f"Starting preprocessing with {chunks} chunks and {timeout}s timeout.")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=fileset,
            step_size=chunks,
            skip_bad_files=False,
            uproot_options={"handler": uproot.XRootDSource, "timeout": timeout}
        )

    logging.info("Preprocessing completed.")
    print()
    return dataset_runnable, dataset_updated

def save_json(output_file, data, data_all):
    """
    Save the processed JSON data to a file. If data and data_all are different,
    throw an error and output the differences. If they are the same, save only data.
    """
    output_path = Path(output_file)

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

    # Check if the file already exists and warn if it will be overwritten
    if output_path.exists():
        logging.warning(f"{output_file} already exists, overwriting.")

    # Save the processed data to the output file
    with open(output_path, 'w') as file:
        json.dump(data, file, indent=4)
    logging.info(f"JSON data successfully saved to {output_file}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("run", type=str, choices=["Run2Summer20UL18", "Run3Summer22"], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("sample", type=str, choices=["bkg"], help="Sample type (bkg, sig, data)")
    parser.add_argument("--umn", action="store_true", help="Enable UMN mode (default: False)")
    parser.add_argument("--chunks", type=int, default=100_000, help="Chunk size for processing")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout for uproot file handling")

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
    if not args.umn:
        input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/Run3Summer22/{args.run}_{args.sample}_cfg.json"
        output_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{args.run}/{args.run}_{args.sample}_preprocessed_skims.json"

    # Load the input JSON file
    try:
        with open(input_file, 'r') as file:
            fileset = json.load(file)
        logging.info(f"Loaded input JSON file from {input_file}")
    except FileNotFoundError:
        logging.error(f"Input file {input_file} not found!")
        exit(1)

    # Clear the "files" content and update with new ROOT files
    fileset = replace_files_in_json(fileset, args.run, args.umn)

    # Preprocess the updated fileset
    dataset_runnable, dataset_updated = preprocess_json(fileset, chunks=args.chunks, timeout=args.timeout)

    # Save the modified JSON to the output file
    save_json(output_file, dataset_runnable, dataset_updated)
