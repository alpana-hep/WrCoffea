import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")

import json
import argparse
import subprocess
import logging
from coffea.dataset_tools import preprocess
from dask.diagnostics import ProgressBar
from pathlib import Path
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, repo_root)

from python.preprocess_utils import get_era_details, load_json, save_json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def replace_files_in_json(data: dict, run: str, year: str, era: str, umn: bool, sample: str) -> dict:
    metadata_keys = (["das_name", "run", "year", "era", "dataset", "physics_group", "datatype"]
                     if sample == "data" 
                     else ["das_name", "run", "year", "era", "dataset", "physics_group", "xsec", "datatype"])

    for key, entry in data.items():
        metadata = {k: entry.pop(k) for k in metadata_keys if k in entry}
        files = entry.pop("files", {})
        data[key] = {"files": files, "metadata": metadata}

    for dataset_name, dataset_info in data.items():
        dataset = dataset_info["metadata"].get("dataset")
        if not dataset:
            logging.warning(f"Dataset not found in metadata for {dataset_name}")
            continue

        root_files = (get_root_files_from_umn(dataset, era) if umn 
                      else get_root_files_from_eos(dataset, run, year, era))

        if root_files:
            for file_path in root_files:
                dataset_info["files"][file_path] = "Events"
        else:
            logging.warning(f"No ROOT files found for dataset {dataset_name}")
    return data

def get_root_files_from_umn(dataset: str, mc_campaign: str) -> list[str]:
    run, year, era = get_era_details(mc_campaign)
    base_path = Path(f"/local/cms/user/jack1851/skims/2025/{run}/{year}/{mc_campaign}/{dataset}/")
    root_files = []
    if base_path.exists():
        for path in base_path.rglob("*.root"):
            root_files.append(str(path))
        logging.info(f"Found {len(root_files)} ROOT files for dataset {dataset}")
    else:
        logging.error(f"Base path '{base_path}' does not exist.")
    return root_files

def get_root_files_from_eos(dataset: str, run: str, year: str, era: str) -> list[str]:
    base_path = f"/store/user/wijackso/WRAnalyzer/skims/2025/{run}/{year}/{era}/{dataset}/"
    cmd = ["xrdfs", "root://cmseos.fnal.gov", "ls", base_path]
    try:
        output = subprocess.check_output(cmd, text=True)
        root_files = [f"root://cmseos.fnal.gov/{line.strip()}" 
                      for line in output.splitlines() if line.endswith(".root")]
        logging.info(f"Found {len(root_files)} ROOT files for dataset {dataset}")
        return root_files
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to list ROOT files for {dataset}: {e}")
        return []

def preprocess_json(fileset: dict, chunks: int = 100_000, timeout: int = 3600):
    logging.info(f"Starting preprocessing with {chunks} chunks and {timeout}s timeout.")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=fileset, step_size=chunks, skip_bad_files=True
        )
    logging.info("Preprocessing completed.")
    return dataset_runnable, dataset_updated

def main():
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("era", type=str,
                        choices=["RunIISummer20UL16", "RunIISummer20UL17", "RunIISummer20UL18",
                                 "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix"],
                        help="Run era (e.g., RunIISummer20UL18)")
    parser.add_argument("sample", type=str, choices=["mc", "data", "signal"],
                        help="Sample type (e.g., mc, data, signal)")
    parser.add_argument("--umn", action="store_true", help="Enable UMN mode")
    parser.add_argument("--chunks", type=int, default=100_000, help="Chunk size for processing")
    parser.add_argument("--timeout", type=int, default=3600, help="Timeout for file handling")
    args = parser.parse_args()

    run, year, era = get_era_details(args.era)
    input_file = Path("data/configs") / run / year / era / f"{era}_{args.sample}.json"
    output_file = Path("data/jsons") / run / year / era / "skimmed" / f"{era}_{args.sample}_preprocessed_skims.json"
    
    fileset = load_json(str(input_file))
    print()
    fileset = replace_files_in_json(fileset, run, year, era, args.umn, args.sample)
    print()
    dataset_runnable, dataset_updated = preprocess_json(fileset, chunks=args.chunks, timeout=args.timeout)
    print()
    save_json(str(output_file), dataset_runnable, dataset_updated)

if __name__ == "__main__":
    main()
