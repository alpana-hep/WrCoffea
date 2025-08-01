#!/usr/bin/env python3

import warnings
warnings.filterwarnings("ignore")

import getpass
import sys
from pathlib import Path

import json
import awkward as ak
import uproot
import hist
import coffea
import numpy as np

from dask.distributed import Client, LocalCluster
from coffea.processor import Runner, DaskExecutor 
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.processor import ProcessorABC

# ensure src/ is importable
repo_root = Path(__file__).resolve().parent
sys.path.insert(0, str(repo_root / "src"))

# import with a safe fallback
from analyzer import WrAnalysis

import logging
logging.getLogger("distributed").setLevel(logging.INFO)
logging.getLogger("coffea").setLevel(logging.DEBUG)


def build_client():
    whoami_output = getpass.getuser()
    if whoami_output == "cms-jovyan":
        return Client("tls://localhost:8786")
    else:
        cluster = LocalCluster(n_workers=1, threads_per_worker=1)
        return Client(cluster)

def load_json_file(path):
    path = Path(path)
    try:
        with path.open() as f:
            return json.load(f)  # returns a dict/list structure
    except FileNotFoundError:
        raise
    except json.JSONDecodeError as e:
        raise ValueError(f"Broken JSON in {path}: {e}") from e

def main():
    NanoAODSchema.warn_missing_crossrefs = False

    client = build_client()

    print(f"awkward: {ak.__version__}")
    print(f"uproot: {uproot.__version__}")
    print(f"hist: {hist.__version__}")
    print(f"coffea: {coffea.__version__}")

    run = Runner(
        executor = DaskExecutor(client=client, compression=None),
        chunksize=250_000,
        maxchunks = None,
        skipbadfiles=True,
        xrootdtimeout = 60,
        align_clusters = False,
        savemetrics=True,
        schema=NanoAODSchema,
    )

    fileset = load_json_file("data/jsons/Run3/2022/Run3Summer22/skimmed/Run3Summer22_mc_lo_dy_skimmed_fileset.json")

    print(fileset)
    preproc_for_run = run.preprocess(fileset=fileset, treename="Events")
    output, metrics = run(preproc_for_run, processor_instance=WrAnalysis(mass_point=None),)

    print("Output:", output)
    print("Metrics:", metrics)


if __name__ == "__main__":
    main()
