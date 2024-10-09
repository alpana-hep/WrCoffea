import json
import time
import warnings
from dask import delayed
from dask.diagnostics import ProgressBar
import awkward as ak
import dask_awkward as dak
import gc
import argparse
from coffea.dataset_tools import preprocess, apply_to_fileset, max_files, max_chunks, slice_files
from coffea.nanoevents import NanoAODSchema
import uproot
from dask.distributed import Client

# Suppress FutureWarnings for better output readability
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea")
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")

def is_rootcompat(a):
    """Check if the data is a flat or 1-d jagged array for compatibility with uproot."""
    t = dak.type(a)
    if isinstance(t, ak.types.NumpyType):
        return True
    if isinstance(t, ak.types.ListType) and isinstance(t.content, ak.types.NumpyType):
        return True
    return False

def uproot_writeable(events):
    """Restrict to columns that uproot can write compactly."""
    out_event = events[list(x for x in events.fields if not events[x].fields)]
    for bname in events.fields:
        if events[bname].fields:
            out_event[bname] = ak.zip(
                {
                    n: ak.without_parameters(events[bname][n])
                    for n in events[bname].fields
                    if is_rootcompat(events[bname][n])
                }
            )
    return out_event

def make_skimmed_events(events):
    """Apply event selection to create skimmed datasets."""
    selected_electrons = events.Electron[(events.Electron.pt > 45)]
    selected_muons = events.Muon[(events.Muon.pt > 45)]
    event_filters = ((ak.count(selected_electrons.pt, axis=1) + ak.count(selected_muons.pt, axis=1)) >= 2)

    skimmed = events[event_filters]
    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x in ["Electron", "Muon", "Jet", "FatJet", "HLT", "event", "run", "luminosityBlock", "genWeight"]))]
    return skimmed_dropped

def load_output_json():
    """Load dataset from JSON file."""
    json_file_path = f'jsons/UL18_bkg_preprocessed.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def extract_data(dataset_dict, dataset, year):
    """Extract data for the given dataset and year from the dataset dictionary."""
    mapping = {
        ("DYJetsToLL_M-50_HT-70to100", "2018"): "/DYJetsToLL_M-50_HT-70to100_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-100to200", "2018"): "/DYJetsToLL_M-50_HT-100to200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-200to400", "2018"): "/DYJetsToLL_M-50_HT-200to400_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-400to600", "2018"): "/DYJetsToLL_M-50_HT-400to600_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-600to800", "2018"): "/DYJetsToLL_M-50_HT-600to800_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-800to1200", "2018"): "/DYJetsToLL_M-50_HT-800to1200_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-1200to2500", "2018"): "/DYJetsToLL_M-50_HT-1200to2500_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("DYJetsToLL_M-50_HT-2500toInf", "2018"): "/DYJetsToLL_M-50_HT-2500toInf_TuneCP5_PSweights_13TeV-madgraphMLM-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM",
        ("TTTo2L2Nu", "2018"): "/TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8/RunIISummer20UL18NanoAODv9-106X_upgrade2018_realistic_v16_L1v1-v1/NANOAODSIM"
    }
    key = mapping.get((dataset, year))
    if key is None:
        raise ValueError(f"Invalid combination of dataset and year: {dataset}, {year}")
    return {key: dataset_dict[key]}

@delayed
def process_file(sliced_dataset, dataset, file_index):
    """Process and skim individual files."""
    skimmed_dict = apply_to_fileset(
        make_skimmed_events,
        sliced_dataset,
        schemaclass=NanoAODSchema,
    )

    with ProgressBar():
        for dataset_name, skimmed in skimmed_dict.items():
            print(f"Calling uproot_writeable and repartition for file {file_index}")
            skimmed = uproot_writeable(skimmed)
            skimmed = skimmed.repartition(rows_per_partition=10000)
            print(f"Writing file {file_index} with uproot.dask_write")
            skimmed = skimmed.persist()
            uproot.dask_write(skimmed, compute=True, destination=f"tmp/{dataset}", prefix=f"{dataset}_skim{file_index}", tree_name="Events")

    # Clean up memory
    gc.collect()
    print(f"File {file_index} processing complete.")

if __name__ == "__main__":
    # Argument parsing
    parser = argparse.ArgumentParser(description='Process dataset and run.')
    parser.add_argument('dataset', type=str, help='Dataset to process')
    parser.add_argument('--start', type=int, default=1, help='File number at which to start')
    args = parser.parse_args()

#    client = Client(n_workers=4, threads_per_worker=1, memory_limit='4GB')

    # Initial time marker
    t0 = time.monotonic()

    # Load the full dataset from JSON and extract relevant data
    fileset = load_output_json()
    full_dataset = extract_data(fileset, args.dataset, "2018")
    dataset_key = list(full_dataset.keys())[0]
    num_files = len(full_dataset[dataset_key]['files'])

    tasks = []

    sliced_dataset = slice_files(full_dataset, slice(args.start - 1, args.start))

    print(f"Skimming file {args.start} of {num_files} for {args.dataset}")
    task = process_file(sliced_dataset, args.dataset, args.start)
    tasks.append(task)

    # Execute all tasks
    results = delayed(tasks).compute()
    exec_time = time.monotonic() - t0
    print(f"File {args.start} skimmed in {exec_time/60:.2f} minutes.\n")
