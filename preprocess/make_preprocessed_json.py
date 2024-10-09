#Gets the root files and makes a json file that can be passed to coffea's skimmer (no need to preprocess)
import json
import os
import sys
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
#import warnings
import subprocess
from coffea.dataset_tools import rucio_utils
from coffea.dataset_tools.dataset_query import print_dataset_query
from rich.console import Console
from rich.table import Table
from coffea.dataset_tools.dataset_query import DataDiscoveryCLI
from dask.diagnostics import ProgressBar
NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False
from coffea.dataset_tools import preprocess, max_chunks, max_files
import uproot
from dask.distributed import Client

#warnings.filterwarnings("error", module="coffea.*")

def get_genevents_from_coffea(rootFile):
    filepath = f"{rootFile}"
    try:
       # Open the ROOT file using NanoEventsFactory
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"},
                schemaclass=NanoAODSchema
        ).events()

        genEventSumw = int(events.genEventSumw.compute()[0])
        print("genEventSumw", genEventSumw)
        return genEventSumw

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0, 0.0, 0.0

def generate_json(config):
    data = {}

    print("Creating json file...")
    for dataset_name, metadata in config.items():
        print("Preparing", dataset_name)

        metadata = {
            "mc_campaign": metadata["mc_campaign"],
            "process": metadata["process"],
            "dataset": metadata["dataset"],
            "xsec": metadata["xsec"],
            "genEventSumw": 0.0,
        }

        data[dataset_name] = metadata

    print(f"\nQuerying replica sites")
    ddc = DataDiscoveryCLI()
    ddc.do_allowlist_sites(["T1_US_FNAL_Disk", "T2_US_Wisconsin", "T2_CH_CERN", "T2_FI_HIP", "T2_UK_London_IC"])
#    ddc.do_blocklist_sites(["T3_KR_UOS", "T2_ES_CIEMAT", "T2_US_Purdue", "T2_UK_SGrid_Bristol", "T2_IN_TIFR", "T2_US_MIT", "T3_IT_Trieste", "T3_KR_KNU", "T2_ES_IFCA", "T2_RU_INR"])
    dataset = ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="round-robin")
    print()

    dataset_runnable, dataset_updated = preprocess_json(dataset)

    for dataset_name, data in dataset_runnable.items():
        print(f"\nCalculcating genEventSumw for {dataset_name}")
        file_paths = list(data['files'].keys())

        for file_path in file_paths:
            genEventSumw = get_genevents_from_coffea(file_path)
            data["metadata"]["genEventSumw"] += genEventSumw

    return dataset_runnable, dataset_updated

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

def save_dict_to_json(data_processed, data_all):
    with open('jsons/UL18_bkg_preprocessed.json', 'w') as json_file:
        json.dump(data_processed, json_file, indent=4)
    print(f"Preprocessed json file saved to jsons/UL18_bkg_preprocessed.json")

    with open('jsons/UL18_bkg_preprocessed_all.json', 'w') as json_file:
        json.dump(data_all, json_file, indent=4)
    print(f"Json file saved to jsons/UL18_bkg_preprocessed_all.json")

def preprocess_json(fileset):
    chunks = 100_000

    print("\nPreprocessing files")
    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=max_files(fileset),
            step_size=chunks,
            skip_bad_files=False,
            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
        )

    print("Preprocessing completed.\n")

    return dataset_runnable, dataset_updated

if __name__ == "__main__":
    client = Client(n_workers=4, threads_per_worker=1, memory_limit='2GB')
    config = load_config("configs/UL18_bkg_cfg.json")
    dataset_runnable, dataset_updated = generate_json(config)
    save_dict_to_json(dataset_runnable, dataset_updated)

