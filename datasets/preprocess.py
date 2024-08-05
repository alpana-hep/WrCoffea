from coffea.dataset_tools import preprocess, max_chunks, max_files
import json
import gzip
import argparse
from dask.diagnostics import ProgressBar

def load_json(filename):
    json_file_path = f'{filename}.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pre-processing script for WR analysis.")
    parser.add_argument("json_file",type=str,help="Json file to preprocess.")
    args = parser.parse_args()

    print(f"Preprocessing {args.json_file}.json")

    fileset = load_json(args.json_file)

    chunks = 100_000

    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=fileset,
            step_size=chunks,
            skip_bad_files=True,
        )

    print("Preprocessing completed. Comparing dataset_runnable and dataset_updated...\n")

    with open(f"{args.json_file}_preprocessed_runnable.json", "w") as file:
        print(f"Saved preprocessed fileset to {args.json_file}_preprocessed_runnable.json")
        json.dump(dataset_runnable, file, indent=2)

    with open(f"{args.json_file}_preprocessed_all.json", "w") as file:
        print(f"Saved preprocessed fileset to {args.json_file}_preprocessed_all.json")
        json.dump(dataset_updated, file, indent=2)
