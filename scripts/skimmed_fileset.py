#!/usr/bin/env python3
#
# -----------------------------------------------------------------------------
# Example usage:
#   # Takes in config JSON, and populates it with a list of skimmed ROOT files from EOS:
#   python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_mc_lo_dy.json
#   python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_data.json
#   python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_signal.json 
#
# These commands will produce:
#   data/jsons/Run3/2022/Run3Summer22/skimmed/Run3Summer22_mc_lo_dy_skimmed_fileset.json
#   data/jsons/Run3/2022/Run3Summer22/skimmed/Run3Summer22_data_skimmed_fileset.json
#   data/jsons/Run3/2022/Run3Summer22/skimmed/Run3Summer22_signal_skimmed_fileset.json
# -----------------------------------------------------------------------------

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea.*")

import json
import argparse
import subprocess
import logging
from pathlib import Path
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, repo_root)

from python.preprocess_utils import get_era_details, load_json

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def replace_files_in_json(data: dict, run: str, year: str, era: str, umn: bool, sample: str) -> dict:
    metadata_keys = (["das_name", "run", "year", "era", "dataset", "physics_group", "datatype"]
                     if sample == "data"
                     else ["das_name", "run", "year", "era", "dataset", "physics_group", "xsec", "datatype", "nevts"])

    for key, entry in data.items():
        metadata = {k: entry.pop(k) for k in metadata_keys if k in entry}
        if "dataset" in entry:
            metadata["sample"] = entry.pop("dataset")

        raw_files = entry.pop("files", {})

        if isinstance(raw_files, dict):
            files_dict = raw_files.copy()
        elif isinstance(raw_files, list):
            files_dict = {fp: "Events" for fp in raw_files}
        else:
            files_dict = {}

        data[key] = {"files": files_dict, "metadata": metadata}

    for ds_name, ds_info in data.items():
        dataset = ds_info["metadata"].get("dataset")
        if not dataset:
            logging.warning(f"Dataset not found in metadata for {ds_name}")
            continue

        root_files = (get_root_files_from_umn(dataset, era) if umn
                      else get_root_files_from_eos(dataset, run, year, era))

        if root_files:
            for fp in root_files:
                ds_info["files"].setdefault(fp, "Events")
        else:
            logging.warning(f"No ROOT files found for dataset {ds_name}")

    return data


def get_root_files_from_umn(dataset: str, mc_campaign: str) -> list[str]:
    # mc_campaign eg. "Run3Summer22"
    run, year, era = get_era_details(mc_campaign)
    base = Path(f"/local/cms/user/jack1851/skims/2025/{run}/{year}/{mc_campaign}/{dataset}/")
    files = []
    if base.exists():
        for p in base.rglob("*.root"):
            files.append(str(p))
        logging.info(f"Found {len(files)} ROOT files for {dataset} in UMN skims")
    else:
        logging.error(f"UMN base path '{base}' not found")
    return files


def get_root_files_from_eos(dataset: str, run: str, year: str, era: str) -> list[str]:
    base_path = f"/store/user/wijackso/WRAnalyzer/skims/2025/{run}/{year}/{era}/{dataset}/"
    cmd = ["xrdfs", "root://cmseos.fnal.gov", "ls", base_path]
    try:
        out = subprocess.check_output(cmd, text=True)
        files = [
            f"root://cmseos.fnal.gov/{line.strip()}"
            for line in out.splitlines() if line.endswith(".root")
        ]
        logging.info(f"Found {len(files)} ROOT files for {dataset} on EOS")
        return files
    except subprocess.CalledProcessError as e:
        logging.error(f"EOS listing failed for {dataset}: {e}")
        return []

def rename_dataset_key_to_sample(data: dict) -> dict:
    for entry in data.values():
        md = entry.get("metadata", {})
        if "dataset" in md:
            md["sample"] = md.pop("dataset")
    return data

def main():
    parser = argparse.ArgumentParser(
        description="Replace file lists in a JSON config and run Coffea preprocessing."
    )
    parser.add_argument(
        "--config",
        type=Path,
        required=True,
        help="Path to the input JSON configuration (e.g. data/configs/.../era_sample.json)"
    )
    parser.add_argument(
        "--umn",
        action="store_true",
        help="Fetch ROOT files from UMN skims instead of EOS"
    )
    args = parser.parse_args()

    input_path = args.config
    if not input_path.is_file():
        logging.error(f"Input file not found: {input_path}")
        sys.exit(1)

    # derive run/year/era from the input path under data/configs
    cfg_dir = input_path.parent  # e.g. data/configs/Run3/2022/Run3Summer22
    cur = cfg_dir
    while cur.name != "configs":
        cur = cur.parent
    data_root = cur.parent  # data/
    rel = cfg_dir.relative_to(data_root / "configs")  # Run3/2022/Run3Summer22
    run, year, era = rel.parts

    # derive sample from filename: should be era_sample.json
    stem = input_path.stem  # e.g. "Run3Summer22_mc"
    prefix = f"{era}_"
    if not stem.startswith(prefix):
        logging.warning(f"Filename '{stem}' doesn't start with '{prefix}'")
    sample = stem[len(prefix):]

    fileset = load_json(str(input_path))
    fileset = replace_files_in_json(fileset, run, year, era, args.umn, sample)
    fileset = rename_dataset_key_to_sample(fileset)

    out_dir = data_root / "jsons" / run / year / era / "skimmed"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_file = out_dir / f"{era}_{sample}_skimmed_fileset.json"
    with out_file.open("w") as f:
        json.dump(fileset, f, indent=2, sort_keys=True)
    logging.info(f"Saved JSON to {out_file}")


if __name__ == "__main__":
    main()
