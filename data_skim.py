import argparse
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import preprocess, apply_to_fileset, max_files, max_chunks
import awkward as ak
import dask_awkward as dak
import dask
from dask.diagnostics import ProgressBar
import uproot
import gzip
import json

def is_rootcompat(a):
    """Is it a flat or 1-d jagged array?"""
    t = dak.type(a)
    if isinstance(t, ak.types.NumpyType):
        return True
    if isinstance(t, ak.types.ListType) and isinstance(t.content, ak.types.NumpyType):
        return True

    return False

def uproot_writeable(events):
    """Restrict to columns that uproot can write compactly"""
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
    # Place your selection logic here
    selected_electrons = events.Electron[(events.Electron.pt > 50)]
    selected_muons = events.Muon[(events.Muon.pt > 50)]
    event_filters = ((ak.count(selected_electrons.pt, axis=1) + ak.count(selected_muons.pt, axis=1)) >= 2)

    skimmed = events[event_filters]
    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x in ["Electron", "Muon", "Jet", "HLT", "event"]))]

    # Returning the skimmed events
    return skimmed_dropped

def load_output_json():
    json_file_path = f'datasets/2018Data_available.json.gz'
    with gzip.open(json_file_path, 'rt') as file:
        data = json.load(file)
    return data

def extract_data(dataset_dict, dataset, year, run):
    # Mapping of dataset, year, and run combinations to their corresponding keys
    mapping = {
        ("SingleMuon", "2018", "RunA"): "/SingleMuon/Run2018A-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD",
        ("SingleMuon", "2018", "RunB"): "/SingleMuon/Run2018B-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD",
        ("SingleMuon", "2018", "RunC"): "/SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD",
        ("SingleMuon", "2018", "RunD"): "/SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        ("EGamma", "2018", "RunA"): "/EGamma/Run2018A-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        ("EGamma", "2018", "RunB"): "/EGamma/Run2018B-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        ("EGamma", "2018", "RunC"): "/EGamma/Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        ("EGamma", "2018", "RunD"): "/EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD"
    }

    # Extract the corresponding key from the mapping
    key = mapping.get((dataset, year, run))

    if key is None:
        raise ValueError(f"Invalid combination of dataset, year, and run: {dataset}, {year}, {run}")

    # Return the corresponding dictionary entry
    return {key: dataset_dict[key]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process dataset, year, and run.')
    parser.add_argument('dataset', choices=['SingleMuon', 'EGamma'], help='Dataset to process')
    parser.add_argument('year', choices=['2018'], help='Year of the dataset')
    parser.add_argument('run', choices=['RunA', 'RunB', 'RunC', 'RunD'], help='Run of the dataset')

    args = parser.parse_args()

    print("Starting to skim events")

    fileset = load_output_json() # All the data files

    dataset = extract_data(fileset, args.dataset, args.year, args.run) # Filtered dataset

    dataset_runnable = max_chunks(max_files(dataset))  # Just 1 chunk of 1 file to test

    print(f"\nFileset:\n{dataset_runnable}\n")

    print("Computing dask task graph")
    skimmed_dict = apply_to_fileset(
        make_skimmed_events,
        dataset_runnable,
        schemaclass=NanoAODSchema,
        uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
    )

    print(f"\nskimmed_dict: {skimmed_dict}\n")

    print("Executing task graph and saving")
    with ProgressBar():
        for dataset, skimmed in skimmed_dict.items():
            skimmed = uproot_writeable(skimmed)
            skimmed = skimmed.repartition(
                rows_per_partition=2500000 # 1000 events per file
            )  # Repartitioning so that output file contains ~100_000 events per partition
            uproot.dask_write(
                skimmed,
                destination="dataskims/",
                prefix=f"{args.year}/{args.dataset}/{args.run}/{args.dataset}{args.year}{args.run}",
            )

