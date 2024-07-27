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

def extract_data(dataset_dict, option):
    # Mapping of options to their corresponding keys in the dataset dictionary
    mapping = {
        "SingleMuon 2018 Run A": "/SingleMuon/Run2018A-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD",
        "SingleMuon 2018 Run B": "/SingleMuon/Run2018B-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD",
        "SingleMuon 2018 Run C": "/SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD",
        "SingleMuon 2018 Run D": "/SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        "EGamma 2018 Run A": "/EGamma/Run2018A-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        "EGamma 2018 Run B": "/EGamma/Run2018B-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        "EGamma 2018 Run C": "/EGamma/Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD",
        "EGamma 2018 Run D": "/EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD"
    }

    # Extract the corresponding key from the mapping
    key = mapping.get(option)

    if key is None:
        raise ValueError(f"Invalid option: {option}")

    # Return the corresponding dictionary entry
    return {key: dataset_dict[key]}

print("Starting to skim events")

fileset = load_output_json() #All the data files

dataset = extract_data(fileset, "SingleMuon 2018 Run A") #Just the SingleMuon 2018 Run A files

dataset_runnable = max_chunks(max_files(dataset, 1))  #Just 1 chunk of 1 file to test

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
            rows_per_partition=4000000 #1000 events per file
        )  # Reparititioning so that output file contains ~100_000 eventspartition
        uproot.dask_write(
            skimmed,
            destination="skimtest/",
            prefix=f"{dataset}_onefilefiltered1/skimmed",
        )
