import json
import argparse
import subprocess
import uproot
import logging
from coffea.dataset_tools import preprocess
from dask.diagnostics import ProgressBar
from pathlib import Path
import difflib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def replace_files_in_json(data):
    """
    Clears 'files' and 'form' entries from the provided JSON data and fetches new file paths.
    """
    for dataset_name, dataset_info in data.items():
        # Clear existing 'files' key
        if "files" in dataset_info:
            dataset_info["files"] = {}

        # Remove 'form' key if it exists
        if "form" in dataset_info:
            del dataset_info["form"]

        # Get the dataset name from metadata
        dataset = dataset_info["metadata"].get("dataset", "")
        root_files = get_root_files_from_eos(dataset)

        if root_files:
            for file_path in root_files:
                dataset_info["files"][file_path] = "Events"
        else:
            logging.warning(f"No ROOT files found for dataset {dataset_name}")

    return data

def get_root_files_from_eos(dataset):
    """
    Use xrdfs to get the list of ROOT files from EOS for a given dataset.
    """
    base_path = f"/store/user/wijackso/skims/UL2018/lep_pt_45/{dataset}/"
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
    parser = argparse.ArgumentParser(description="Clear 'files' content in the input JSON file.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file")
    parser.add_argument("output_file", type=str, help="Path to the output JSON file")
    parser.add_argument("--chunks", type=int, default=100_000, help="Chunk size for processing")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout for uproot file handling")

    # Parse the arguments
    args = parser.parse_args()

    # Load the input JSON file
    try:
        with open(args.input_file, 'r') as file:
            fileset = json.load(file)
        logging.info(f"Loaded input JSON file from {args.input_file}")
    except FileNotFoundError:
        logging.error(f"Input file {args.input_file} not found!")
        exit(1)

    # Clear the "files" content and update with new ROOT files
    fileset = replace_files_in_json(fileset)

    # Preprocess the updated fileset
    dataset_runnable, dataset_updated = preprocess_json(fileset, chunks=args.chunks, timeout=args.timeout)

    # Save the modified JSON to the output file
    save_json(args.output_file, dataset_runnable, dataset_updated)
