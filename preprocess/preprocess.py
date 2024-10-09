import json
import sys
import subprocess
import warnings
from coffea.dataset_tools import rucio_utils
from coffea.dataset_tools.dataset_query import print_dataset_query
from rich.console import Console
from rich.table import Table
from coffea.dataset_tools.dataset_query import DataDiscoveryCLI
from coffea.dataset_tools import preprocess, max_chunks, max_files
from dask.diagnostics import ProgressBar
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

NanoAODSchema.error_missing_event_ids= False
warnings.filterwarnings("ignore", module="coffea")

def get_genevents_from_coffea(filepath):
    try:
       # Open the ROOT file using NanoEventsFactory
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"}, 
                schemaclass=NanoAODSchema
        ).events()

        # Calculate the genEventCount, genEventSumw, and genEventSumw2
        genEventCount = int(events.genEventCount.compute()[0])
        genEventSumw = int(events.genEventSumw.compute()[0])
        genEventSumw2 = int(events.genEventSumw2.compute()[0])
        return genEventCount, genEventSumw, genEventSumw2

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0, 0.0, 0.0

def query_das(das_name):
    command = f'dasgoclient -query="file dataset={das_name}"'
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    files = result.stdout.strip().split('\n')
    return files

def parse_txt_file(config):
    data = {}

    for dataset_name, metadata in config.items():
        print("Preprocessing", dataset_name)
        files = query_das(dataset_name)
        print("files", files)
        files_with_prefix = [f'root://cmsxrootd.fnal.gov/{file}' for file in files if file]
        dataset_data = {
                "mc_campaign": "UL2018",
                "process": metadata["process"],
                "dataset": metadata["dataset"],
                "xsec": metadata["xsec"],
                "genEventCount": 0,
                "genEventSumw": 0.0,
                "genEventSumw2": 0.0
        }

        for file in files_with_prefix:
            genEventCount, genEventSumw, genEventSumw2 = get_genevents_from_coffea(file)
            dataset_data["genEventCount"] += genEventCount
            dataset_data["genEventSumw"] += genEventSumw
            dataset_data["genEventSumw2"] += genEventSumw2
        data[dataset_name] = dataset_data

    return data

def write_json_file(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    config = load_config("configs/DY_UL18_cfg.json")
    data = parse_txt_file(config)

    ddc = DataDiscoveryCLI()
    ddc.do_allowlist_sites(["T1_US_FNAL_Disk", "T2_US_Wisconsin", "T2_CH_CERN", "T2_FI_HIP", "T2_UK_London_IC"])

    with ProgressBar():
        dataset_runnable, dataset_updated = preprocess(
            fileset=ddc.load_dataset_definition(dataset_definition = data, query_results_strategy="all", replicas_strategy="round-robin"),
            step_size=100_000,
            skip_bad_files=False,
        )

    with open(f"test_preprocessed_runnable.json", "w") as file:
        print(f"Saved preprocessed fileset to test_preprocessed_runnable.json")
        json.dump(dataset_runnable, file, indent=2)
