import argparse
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import preprocess, apply_to_fileset, max_files, max_chunks, slice_files
import awkward as ak
import dask_awkward as dak
import dask
from dask.diagnostics import ProgressBar
from dask.distributed import Client, LocalCluster
#from lpcjobqueue import LPCCondorCluster
import uproot
import gzip
import json
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning, module="coffea")
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")
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
    selected_electrons = events.Electron[(events.Electron.pt > 45)]
    selected_muons = events.Muon[(events.Muon.pt > 45)]
    event_filters = ((ak.count(selected_electrons.pt, axis=1) + ak.count(selected_muons.pt, axis=1)) >= 2)

    skimmed = events[event_filters]
    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x in ["Electron", "Muon", "Jet", "FatJet", "HLT", "event", "run", "luminosityBlock"]))]
#    skimmed_dropped = skimmed
    return skimmed_dropped

def load_output_json():
    json_file_path = f'data/UL2018_Data_preprocessed_runnable.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def extract_data(dataset_dict, dataset, year, run):
    mapping = {
        ("SingleMuon", "2018", "RunA"): "/SingleMuon/Run2018A-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD", #92 files
        ("SingleMuon", "2018", "RunB"): "/SingleMuon/Run2018B-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD", #51 files
        ("SingleMuon", "2018", "RunC"): "/SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD", #56 files
        ("SingleMuon", "2018", "RunD"): "/SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD", #194 files
        ("EGamma", "2018", "RunA"): "/EGamma/Run2018A-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD", #226 files
        ("EGamma", "2018", "RunB"): "/EGamma/Run2018B-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD", #74 files
        ("EGamma", "2018", "RunC"): "/EGamma/Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD", #83 files
        ("EGamma", "2018", "RunD"): "/EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD" #355 files
    }

    key = mapping.get((dataset, year, run))

    if key is None:
        raise ValueError(f"Invalid combination of dataset, year, and run: {dataset}, {year}, {run}")

    return {key: dataset_dict[key]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process dataset, year, and run.')
    parser.add_argument('dataset', choices=['SingleMuon', 'EGamma'], help='Dataset to process')
    parser.add_argument('year', choices=['2018'], help='Year of the dataset')
    parser.add_argument('run', choices=['RunA', 'RunB', 'RunC', 'RunD'], help='Run of the dataset')
    parser.add_argument('--start', type=int, default=1, help='File number at which to start')

    args = parser.parse_args()

    t0 = time.monotonic()

    print("Starting to skim events\n")

    fileset = load_output_json()

    full_dataset = extract_data(fileset, args.dataset, args.year, args.run)
    dataset_key = list(full_dataset.keys())[0]
    num_files = len(full_dataset[dataset_key]['files'].keys())

    for i in range(args.start-1, args.start+1):
        t0 = time.monotonic()
        print(f"Analyzing file {i+1}")
        sliced_dataset = slice_files(full_dataset, slice(i, i+1))

        print("Computing dask task graph")
        skimmed_dict = apply_to_fileset(
            make_skimmed_events,
            sliced_dataset,
            schemaclass=NanoAODSchema,
            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
            )

        with ProgressBar():
            for dataset, skimmed in skimmed_dict.items():
                print("Calling uproot_writeable and skimmed.repartition")
                skimmed = uproot_writeable(skimmed)
                skimmed = skimmed.repartition(rows_per_partition=2000000)
                print("Calling uproot.dask_write")
                uproot.dask_write(skimmed, compute=True, destination="dataskims/", prefix=f"{args.dataset}{args.year}{args.run}lepPt45/{args.dataset}{args.year}{args.run}_file{i+1}", tree_name = "Events")

        exec_time = time.monotonic() - t0
        print(f"File {i+1} took {exec_time/60:.2f} minutes to skim\n")
