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
import multiprocessing
from pathlib import Path
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.dataset_tools import rucio_utils, preprocess, max_files, max_chunks
from coffea.dataset_tools.dataset_query import print_dataset_query, DataDiscoveryCLI
from rich.console import Console
from rich.table import Table
import os
NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Process the JSON configuration file.")
    parser.add_argument("mc_campaign", type=str, choices=["Run2Autumn18", "Run2Summer20UL18", "Run3Summer22"], help="Run (e.g., Run2UltraLegacy)")
    parser.add_argument("sample", type=str, choices=["bkg", "sig", "data"], help="Sample type (bkg, sig, data)")

    # Parse the arguments
    args = parser.parse_args()

    # Build input and output file paths based on the arguments
    input_file = f"/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/{args.mc_campaign}/{args.mc_campaign}_{args.sample}_datasets.txt"
    output_dir = f"/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/{args.mc_campaign}"

    # Load the configuration file
    with open(input_file, 'r') as file:
        dataset_paths = file.readlines()

    file_contents = ""
    us_redirector = "root://cmsxrootd.fnal.gov/"
    for dataset in dataset_paths:
        dataset = dataset.strip()
        print(f'Finding files for {dataset}')

        result = subprocess.run(['dasgoclient', '-query', f'file dataset={dataset}'], capture_output=True, text=True)

        files = result.stdout.strip().split('\n')
        prepended_files = [f'{us_redirector}{file}' for file in files]

        dataset_name = dataset.split('/')[1]
        print(dataset_name)
        output_txt_path = os.path.join(output_dir, f"{dataset_name}_MINIAOD_files.txt")
        # Write the prepended file paths to the output file
        with open(output_txt_path, 'w') as txt_file:
            for line in prepended_files:
                txt_file.write(f'{line}\n')
        
        print(f"File list saved to {output_txt_path}")
