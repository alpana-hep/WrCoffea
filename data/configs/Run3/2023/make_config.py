import subprocess
import json
import sys
import time

INPUT_JSON = "Run3Summer22EENanoAODv12.json"
OUTPUT_JSON = "Run3Summer22EE.json"
DAS_TIMEOUT = 60  # Timeout in seconds to prevent hanging

def query_das(dataset_name):
    """
    Queries DAS for a given dataset and retrieves metadata.
    Retries every 5 seconds indefinitely if DAS hangs or fails.
    """
    command = f"dasgoclient --query=\"dataset dataset={dataset_name}\" --format=json"
    while True:  # Infinite loop for retrying
        print(f"Running command: {command}")  # Debugging output

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=DAS_TIMEOUT)

            # Print stderr if any errors occur
            if result.stderr:
                print(f"Command Error:\n{result.stderr}", file=sys.stderr)

            # If DAS returns a non-zero exit code, retry
            if result.returncode != 0:
                print(f"Error querying DAS (Exit Code {result.returncode}). Retrying in 5 seconds...", file=sys.stderr)
                time.sleep(5)
                continue  # Retry

            # Try parsing JSON output
            try:
                das_data = json.loads(result.stdout)
                
                # Ensure 'data' field exists and contains dataset information
                if not das_data.get("data"):
                    print(f"No results found for dataset: {dataset_name}. Retrying in 5 seconds...", file=sys.stderr)
                    time.sleep(5)
                    continue  # Retry
                
                # Iterate over 'data' array to find the dataset block with the correct metadata
                for entry in das_data["data"]:
                    dataset_list = entry.get("dataset", [])
                    for dataset in dataset_list:
                        if "primary_ds_name" in dataset:  # This indicates a valid dataset entry
                            return dataset
                
                print(f"No valid dataset details found for {dataset_name}. Retrying in 5 seconds...", file=sys.stderr)
                time.sleep(5)
                continue  # Retry

            except json.JSONDecodeError:
                print("Failed to parse JSON output from DAS. Retrying in 5 seconds...", file=sys.stderr)
                time.sleep(5)
                continue  # Retry

        except subprocess.TimeoutExpired:
            print("DAS query timed out. Retrying in 5 seconds...", file=sys.stderr)
            time.sleep(5)
            continue  # Retry

def process_datasets():
    """
    Reads dataset names from the input JSON file, queries DAS, and writes the results to output JSON.
    """
    try:
        with open(INPUT_JSON, "r") as infile:
            dataset_dict = json.load(infile)
    except FileNotFoundError:
        print(f"Error: File {INPUT_JSON} not found.", file=sys.stderr)
        return
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON file {INPUT_JSON}.", file=sys.stderr)
        return

    output_data = {}

    for dataset_name, dataset_info in dataset_dict.items():
        print(f"Processing dataset: {dataset_name}")
        
        # Query DAS for metadata (will keep retrying if DAS hangs or fails)
        das_metadata = query_das(dataset_name)

        if not das_metadata:
            print(f"Skipping dataset {dataset_name} due to missing DAS data.", file=sys.stderr)
            continue

        # Merge DAS metadata with input JSON data
        merged_data = {
            "das_name": dataset_name,
            "run": "Run3",
            "year": "2022",
            "era": "Run3Summer22EE",
            "dataset": das_metadata.get("primary_ds_name", ""),
            "physics_group": dataset_info.get("physics_group_name", ""),
            "xsec": dataset_info.get("crosssection", 0),  # Keep original "xsec" value
#            "das_id": das_metadata.get("dataset_id", 0),
            "datatype": das_metadata.get("primary_ds_type", ""),
#            "das_name": dataset_name,
        }

        output_data[dataset_name] = merged_data

    # Write output to JSON file
    with open(OUTPUT_JSON, "w") as outfile:
        json.dump(output_data, outfile, indent=4)

    print(f"Output written to {OUTPUT_JSON}")

if __name__ == "__main__":
    process_datasets()
