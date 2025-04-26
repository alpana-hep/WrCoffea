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

from analyzer import WrAnalysis
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
    parser.add_argument("--sample", type=str, choices=["DYJets", "TTbar", "tW", "WJets", "SingleTop", "TTbarSemileptonic", "TTX", "Diboson", "Triboson", "EGamma", "Muon", "Signal"], help="MC sample to analyze (e.g., Signal, DYJets).")

    optional = parser.add_argument_group("Optional arguments")
    optional.add_argument("--extract_reweights", type=str, help="Derive an MC/Data bin-by-bin correction for DYJets and Data based on a histogram variable (e.g. dijet mass). The output is a JSON file with the extracted weights", default=None)
    optional.add_argument("--sf-file", help="path to JSON file of precomputed dijet SFs; if omitted, --derive-sf mode will write this file.", default=None)

    optional.add_argument("--mass", type=str, default=None, choices=MASS_CHOICES, help="Signal mass point to analyze.")

    optional.add_argument("--dir", type=str, default=None, help="Create a new output directory.")
    optional.add_argument("--name", type=str, default=None, help="Append the filenames of the output ROOT files.")


    optional.add_argument("--debug", action='store_true', help="Debug mode (don't compute histograms)")
    args = parser.parse_args()

    print()
    logging.info(f"Analyzing {args.era} - {args.sample} events")
    
    validate_arguments(args)
    run, year, era = get_era_details(args.era)

   # 1) load & merge JSONs
    if args.extract_reweights:
        data_fp = Path("data/jsons") / run / year / era / "skimmed" / f"{era}_data_preprocessed_skims.json"
        mc_fp   = Path("data/jsons") / run / year / era / "skimmed" / f"{era}_mc_preprocessed_skims.json"
        data_fs = load_json(str(data_fp))
        mc_fs   = load_json(str(mc_fp))
        preprocessed_fileset = {**data_fs, **mc_fs}

        # 2) pick only the three samples we need
        samples_to_keep = {"DYJets", "EGamma", "Muon"}
        filtered_fileset = {
            dskey: dsinfo
            for dskey, dsinfo in preprocessed_fileset.items()
            if dsinfo["metadata"]["physics_group"] in samples_to_keep
        }

        # 3) set up WrAnalysis to only fill the two DY‐control regions
        proc = WrAnalysis(
            mass_point=args.mass,
            extract_wghts = args.extract_reweights,
        )

    else:
        # your original single‐JSON logic
        if args.sample in ("EGamma", "Muon"):
            json_name = f"{era}_data_preprocessed_skims.json"
        elif args.sample == "Signal":
            json_name = f"{era}_signal_preprocessed_skims.json"
        else:
            json_name = f"{era}_mc_preprocessed_skims.json"

        filepath = Path("data/jsons") / run / year / era / "skimmed" / json_name
        preprocessed_fileset = load_json(str(filepath))
        filtered_fileset = filter_by_process(preprocessed_fileset, args.sample, args.mass)

        proc = WrAnalysis(
            mass_point=args.mass,
        )

    # 4) build the dask/Coffea pipeline
    to_compute = apply_to_fileset(
        data_manipulation=proc,
        fileset=max_files(max_chunks(filtered_fileset, 1), 1),
        schemaclass=NanoAODSchema,
    )

    t0 = time.monotonic()

    if args.extract_reweights:
        # compute only the two DYCR histograms
        with ProgressBar():
            (out_cr,) = dask.compute(to_compute)

        # find the DYJets entry
        for dsname, hdict in out_cr.items():
            if "DYJets" in dsname:
                hist_mass = hdict["mass_dijet"]
                break
        else:
            raise RuntimeError("No DYJets sample found in CR output")

        # derive & write your SF JSON
        sf_file = f'{args.extract_reweights}_sf.json'
        sf_data = proc.derive_and_export_sf(hist_mass, sf_file)
        logging.info(f"Wrote SFs to {sf_file}")

    else:
        if not args.debug:
            save_hists(to_compute)

    elapsed = (time.monotonic() - t0) / 60
    logging.info(f"Execution took {elapsed:.2f} minutes")
