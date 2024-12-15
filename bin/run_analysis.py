import argparse
import time
import json
import logging
import csv
from pathlib import Path
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, max_files

import sys
import os

# Add the src/ directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python`')))
# Add the parent directory (project_root) to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer import WrAnalysis
from dask.distributed import Client
from dask.diagnostics import ProgressBar
import dask
import uproot
import warnings
import python

# Set up logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress specific warnings
NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")

def load_masses_from_csv(file_path):
    """Load mass points from a CSV file where the first column is WR and the second column is N."""
    mass_choices = []
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  # Skip the header row
            for row in csv_reader:
                if len(row) >= 2:  # Ensure the row has at least two columns
                    wr_mass = row[0].strip()
                    n_mass = row[1].strip()
                    mass_choice = f"WR{wr_mass}_N{n_mass}"
                    mass_choices.append(mass_choice)
        logging.info(f"Loaded {len(mass_choices)} mass points from {file_path}")
    except FileNotFoundError:
        logging.error(f"Mass CSV file not found at: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise
    return mass_choices

def load_json(args):
    sample = args.sample
    run = args.run 
    skimmed = args.skimmed
    umn = args.umn
    """Load the appropriate JSON file based on sample, run, and year."""
    if "EGamma" in sample or "SingleMuon" in sample:
        filepath = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{run}/{run}_data_skimmed.json"
    elif "Signal" in sample:
        filepath = f"data/jsons/{run}/{run}_sig_preprocessed_skims.json"
    else:
        if skimmed and not umn:
            filepath = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{run}/{run}_bkg_skimmed.json"
        elif umn:
            filepath = f"/local/cms/user/jack1851/WrCoffea/data/jsons/{run}/{run}_bkg_preprocessed_skims.json" 
        else:
            filepath = f"/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{run}/{run}_bkg_preprocessed.json"
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
        logging.info(f"Successfully loaded file: {filepath}")
        return data
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {filepath}")
        return None

def filter_by_process(fileset, desired_process, mass=None):
    """Filter fileset based on process type and mass."""
    if desired_process == "Data":
        return fileset
    elif desired_process == "Signal":
        return {ds: data for ds, data in fileset.items() if mass in  data['metadata']['dataset']}
    else:
        return {ds: data for ds, data in fileset.items() if data['metadata']['process'] == desired_process}

def validate_arguments(args):
    """ Validate signal and mass argument consistency """
    if args.sample == "Signal" and not args.mass:
        logging.error("For 'Signal', you must provide a --mass argument (e.g. --mass MWR3000_MN1600).")
        raise ValueError("Missing mass argument for Signal sample.")
    if args.sample != "Signal" and args.mass:
        logging.error("The --mass option is only valid for 'Signal' samples.")
        raise ValueError("Mass argument provided for non-signal sample.")
    logging.info("Arguments validated successfully.")

def setup_lpc_cluster():
    """Set up LPC cluster and return the client."""
    from lpcjobqueue import LPCCondorCluster
    cluster = LPCCondorCluster(cores=1, memory='8GB', log_directory='/uscms/home/bjackson/logs')
    cluster.scale(200)
    client = Client(cluster)
    logging.info("LPC Cluster started.")
    return client, cluster

def run_analysis(args, preprocessed_fileset):
    """Run the main analysis logic."""
    t0 = time.monotonic()
    filtered_fileset = filter_by_process(preprocessed_fileset, args.sample, args.mass)

    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(mass_point=args.mass),
        fileset=max_files(max_chunks(filtered_fileset)),
        schemaclass=NanoAODSchema,
    )

    if args.hists:
        logging.info("Computing histograms...")
        with ProgressBar():
            (histograms,) = dask.compute(to_compute)
        python.save_hists.save_histograms(histograms, args)

    exec_time = time.monotonic() - t0
    logging.info(f"Execution took {exec_time/60:.2f} minutes")

if __name__ == "__main__":

    file_path = Path('data/Run2Autumn18_mass_points.csv')
    MASS_CHOICES = load_masses_from_csv(file_path)

    # Initialize argparse
    parser = argparse.ArgumentParser(description="Processing script for WR analysis.")

    # Required arguments
    parser.add_argument("run", type=str, choices=["Run2Autumn18", "Run2Summer20UL18", "Run3Summer22"], help="Campaign to analyze.")
    parser.add_argument("sample", type=str, choices=["DYJets", "tt", "tW", "Nonprompt", "Other", "EGamma", "SingleMuon", "Signal"],
                        help="MC sample to analyze (e.g., Signal, DYJets).")

    # Optional arguments
    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument("--skimmed", action='store_true', help="Use the skimmed files.")
    optional.add_argument("--lpc", action='store_true', help="Start an LPC cluster.")
    optional.add_argument("--hists", action='store_true', help="Output histograms.")
    optional.add_argument("--umn", action="store_true", help="Enable UMN mode (default: False)")
    optional.add_argument("--mass", type=str, default=None, choices=MASS_CHOICES, help="Signal mass point to analyze.")

    args = parser.parse_args()

    # Load mass choices from the CSV file
    file_path = Path('data/Run2Autumn18_mass_points.csv')
    MASS_CHOICES = load_masses_from_csv(file_path)

    # Validate the parsed arguments
    validate_arguments(args)

    # Load the fileset based on parsed arguments
    preprocessed_fileset = load_json(args)

    # Set up and run analysis with or without LPC cluster
    if args.lpc:
        client, cluster = setup_lpc_cluster()
        try:
            run_analysis(args, preprocessed_fileset)
        finally:
            client.close()
            cluster.close()
    else:
        run_analysis(args, preprocessed_fileset)
