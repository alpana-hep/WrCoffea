import json
import time
import warnings
from dask import delayed
from dask.diagnostics import ProgressBar
import awkward as ak
import dask_awkward as dak
import gc
import argparse
import uproot
from dask.distributed import Client

# Suppress FutureWarnings for better output readability
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea")
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")
warnings.simplefilter("ignore", category=FutureWarning)

from coffea.dataset_tools import preprocess, apply_to_fileset, max_files, max_chunks, slice_files
from coffea.nanoevents import NanoAODSchema

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
#    selected_jets = events.Jet[(events.Jet.pt > 25)]
    event_filters = (
            ((ak.count(selected_electrons.pt, axis=1) + ak.count(selected_muons.pt, axis=1)) >= 2) 
#           & (ak.count(selected_jets.pt, axis=1) >= 2)
            )

    skimmed = events[event_filters]
    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x in ["Electron", "Muon", "Jet", "FatJet", "HLT", "event", "run", "luminosityBlock", "genWeight"]))]
    return skimmed_dropped

def extract_data(dataset_dict, dataset, run):
    """Extract data for the given dataset and year from the JSON config."""

    config_path=f"/uscms/home/bjackson/nobackup/WrCoffea/data/configs/{run}/{run}_bkg_cfg.json"

    with open(config_path, 'r') as f:
        dataset_mapping = json.load(f)

    found_dataset = None
    for key, details in dataset_mapping.items():
        if details['dataset'] == dataset:
            found_dataset = key
            break

    if found_dataset is None:
        raise ValueError(f"Dataset {dataset} not found in the config file")

    return {found_dataset: dataset_dict[found_dataset]}

def process_file(sliced_dataset, dataset_key, dataset, file_index, run):
    """Process and skim individual files."""
    # Access the list of files for the dataset
    file_names = sliced_dataset[dataset_key]['files']
    # Print the file name being processed
    print(f"Processing file: {list(file_names.keys())[0]}")

    """Process and skim individual files."""
    skimmed_dict = apply_to_fileset(
        make_skimmed_events,
        sliced_dataset,
        schemaclass=NanoAODSchema,
        uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
    )

    with ProgressBar():
        for dataset_name, skimmed in skimmed_dict.items():
            conv = uproot_writeable(skimmed)
            uproot.dask_write(conv.repartition(rows_per_partition=50000), compute=True, destination=f"/uscms/home/bjackson/nobackup/WrCoffea/test/{run}/{dataset}", prefix=f"{dataset}_skim{file_index}", tree_name="Events") #10000

    gc.collect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process dataset and run.')
    parser.add_argument('mc_campaign', type=str, help='MC Campaign')
    parser.add_argument('dataset', type=str, help='Dataset to process')
    parser.add_argument('--start', type=int, default=1, help='File number at which to start')
    args = parser.parse_args()

    t0 = time.monotonic()

    json_file_path = f'/uscms/home/bjackson/nobackup/WrCoffea/data/jsons/{args.mc_campaign}/{args.mc_campaign}_bkg_preprocessed.json'
    with open(json_file_path, 'r') as file:
        fileset = json.load(file)

    full_dataset = extract_data(fileset, args.dataset, args.mc_campaign)
    dataset_key = list(full_dataset.keys())[0]
    num_files = len(full_dataset[dataset_key]['files'])

    sliced_dataset = slice_files(full_dataset, slice(args.start - 1, args.start))

    print(f"Skimming file {args.start} of {num_files} for {args.dataset}")
    task = process_file(sliced_dataset, dataset_key, args.dataset, args.start, args.mc_campaign)

    exec_time = time.monotonic() - t0
    print(f"File {args.start} skimmed in {exec_time/60:.2f} minutes.\n")
