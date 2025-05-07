import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")
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

# Add the src/, data/, and python/ directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../data')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python`')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from analyzer_cutflow import WrAnalysis
from dask.distributed import Client
from dask.diagnostics import ProgressBar
import dask
import uproot
from python.save_hists import save_histograms
from python.preprocess_utils import get_era_details, load_json

# Set up logging configuration
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Suppress specific warnings
NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

def load_masses_from_csv(file_path):
    mass_choices = []
    try:
        with open(file_path, mode='r') as file:
            csv_reader = csv.reader(file)
            next(csv_reader)  
            for row in csv_reader:
                if len(row) >= 2:
                    wr_mass = row[0].strip()
                    n_mass = row[1].strip()
                    mass_choice = f"WR{wr_mass}_N{n_mass}"
                    mass_choices.append(mass_choice)
#        logging.info(f"Loaded {len(mass_choices)} mass points from {file_path}")
    except FileNotFoundError:
        logging.error(f"Mass CSV file not found at: {file_path}")
        raise
    except Exception as e:
        logging.error(f"Error loading CSV file: {e}")
        raise
    return mass_choices

def filter_by_process(fileset, desired_process, mass=None):
    if desired_process == "Signal":
        return {ds: data for ds, data in fileset.items() if mass in data['metadata']['dataset']}
    else:
        return {ds: data for ds, data in fileset.items() if data['metadata']['physics_group'] == desired_process}

def validate_arguments(args):
    if args.sample == "Signal" and not args.mass:
        logging.error("For 'Signal', you must provide a --mass argument (e.g. --mass MWR3000_MN1600).")
        raise ValueError("Missing mass argument for Signal sample.")
    if args.sample != "Signal" and args.mass:
        logging.error("The --mass option is only valid for 'Signal' samples.")
        raise ValueError("Mass argument provided for non-signal sample.")
#    logging.info("Arguments validated successfully.")

def run_analysis(args, filtered_fileset):
    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(mass_point=args.mass, sf_file=args.sf_file),
        fileset=max_files(max_chunks(filtered_fileset,),),
        schemaclass=NanoAODSchema,
    )
    return to_compute

def save_hists(to_compute):
    logging.info("Computing histograms...")
    with ProgressBar():
        (histograms,) = dask.compute(to_compute)
    save_histograms(histograms, args)

if __name__ == "__main__":
    file_path = Path('data/RunIISummer20UL18_mass_points.csv')
    MASS_CHOICES = load_masses_from_csv(file_path)

    parser = argparse.ArgumentParser(description="Processing script for WR analysis.")
    parser.add_argument("era", type=str, choices=["RunIISummer20UL16", "RunIISummer20UL17", "RunIISummer20UL18", "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix"], help="Campaign to analyze.")
    parser.add_argument("sample", type=str, choices=["DYJets", "TTbar", "tW", "WJets", "SingleTop", "TTbarSemileptonic", "TTX", "Diboson", "Triboson", "EGamma", "Muon", "Signal"], help="MC sample to analyze (e.g., Signal, DYJets).")
    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument("--mass", type=str, default=None, choices=MASS_CHOICES, help="Signal mass point to analyze.")
    optional.add_argument("--dir", type=str, default=None, help="Create a new output directory.")
    optional.add_argument("--name", type=str, default=None, help="Append the filenames of the output ROOT files.")
    optional.add_argument("--debug", action='store_true', help="Debug mode (don't compute histograms)")
    optional.add_argument("--sf-file", type=str, default=None, help="Path to mass_dijet_sf.json for DY reweights")
    args = parser.parse_args()

    print()
    logging.info(f"Analyzing {args.era} - {args.sample} events")
    
    validate_arguments(args)
    run, year, era = get_era_details(args.era)

    if "EGamma" in args.sample or "Muon" in args.sample:
        filepath = Path("data/jsons") / run / year / era / "skimmed" / f"{era}_data_preprocessed_skims_run3.json"
    elif "Signal" in args.sample:
        filepath = Path("data/jsons") / run / year / era / "skimmed" / f"{era}_signal_preprocessed_skims.json"
    else:
        filepath = Path("data/jsons") / run / year / era / "skimmed" / f"{era}_mc_preprocessed_skims_run3.json"

    preprocessed_fileset = load_json(str(filepath))
    filtered_fileset = filter_by_process(preprocessed_fileset, args.sample, args.mass)

    t0 = time.monotonic()
    to_compute = run_analysis(args, filtered_fileset)

    if not args.debug:
        save_hists(to_compute)
    exec_time = time.monotonic() - t0
    logging.info(f"Execution took {exec_time/60:.2f} minutes")
