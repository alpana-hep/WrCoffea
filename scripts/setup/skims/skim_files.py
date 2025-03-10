import json
import sys
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
import os 

import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea")
warnings.filterwarnings("ignore", category=RuntimeWarning, module="coffea.*")

from coffea.nanoevents import NanoEventsFactory, NanoAODSchema

# Suppress FutureWarnings for better output readability
warnings.filterwarnings("ignore", category=FutureWarning, module="coffea")
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")
warnings.simplefilter("ignore", category=FutureWarning)

from coffea.dataset_tools import preprocess, apply_to_fileset, max_files, max_chunks, slice_files

NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

from coffea.nanoevents import NanoAODSchema

NanoAODSchema.warn_missing_crossrefs = False
NanoAODSchema.error_missing_event_ids = False

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


def get_genevents_from_coffea(rootFile):
    filepath = f"{rootFile}"
    try:
        events = NanoEventsFactory.from_root(
                {filepath: "Runs"},
                schemaclass=NanoAODSchema
        ).events()

        if not hasattr(events, "genEventSumw"):
            print(f"File {filepath} does not contain 'genEventSumw'. Skipping...", file=sys.stderr)
            return 0  # Return 0 so that it doesn't affect the sum

        event_count = events.genEventCount.compute()[0]
        return events.genEventSumw.compute()[0], event_count

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0  # Return 0 on error

def get_data_events(rootFile):
    filepath = f"{rootFile}"
    try:
        events = NanoEventsFactory.from_root(
                {filepath: "Events"},
                schemaclass=NanoAODSchema
        ).events()

        if not hasattr(events, "event"):
            print(f"File {filepath} does not contain 'event'. Skipping...", file=sys.stderr)
            return 0  # Return 0 so that it doesn't affect the sum

        total_events = dak.num(events, axis=0).compute()
        return total_events

    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0  # Return 0 on error

def make_skimmed_events(events):
    """Apply event selection to create skimmed datasets."""

    leptons = ak.with_name(ak.concatenate((events.Electron, events.Muon), axis=1), 'PtEtaPhiMCandidate')
    sorted_indices = ak.argsort(leptons.pt, axis=1, ascending=False)
    leptons = leptons[sorted_indices]
    leptons_padded = ak.pad_none(leptons, 2, clip=True)
    leading_lepton = leptons_padded[:, 0]
    subleading_lepton = leptons_padded[:, 1]

    event_filters = (
        (ak.fill_none(leading_lepton.pt, 0) > 52) &
        (ak.fill_none(subleading_lepton.pt, 0) > 45)
    ) #52 and 45

    print(f"\n### **Skim Details**")
    print(f"-------------------------------------------")
    print("**Leading lepton pT:** 52 GeV")
    print("**SubLeading lepton pT:** 45 GeV")
    print("**Branches:** All")
    print(f"-------------------------------------------")

    # Apply event selection
    skimmed = events[event_filters]

#    drop = [
#            "L1", "SV", "TrigObj", "Tau", "PuppiMET", "Photon", "LowPtElectron", 
#            "IsoTrack", "GenVisTau", "boostedTau", "HTXS"
#            ]
    # Keep only the selected branches
#    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x not in drop))]

    # List of branches to keep
#    keep = [
#            "LHEScaleWeight", "LHEWeight", "run", "GenJet", "GenDressedLepton", "LHE",
#            "HLT", "LHEPdfWeight", "Muon", "GenJetAK8", "PV", "Generator",
#            "SubGenJetAK8", "luminosityBlock", "event", "FatJet", "genWeight",
#            "SubJet", "Jet", "Flag", "LHEPart", "LHEReweightingWeight", "Electron", "Rho"
#    ]

#    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x in keep))]
#    return skimmed_dropped
    return skimmed
#
def extract_data(dataset_dict, dataset, run):
    """Extract data for the given dataset and year from the JSON config."""
    config_path=f"data/configs/{run[:4]}/{run}/{run}_bkg_cfg.json"

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

def filter_json_by_primary_ds_name(json_data, primary_ds_name):
    filtered_data = {
        key: value for key, value in json_data.items()
        if "metadata" in value and value["metadata"].get("dataset") == primary_ds_name
    }
    return filtered_data

def process_file(sliced_dataset, dataset_key, dataset, file_index, era, run):
    """Process and skim individual files."""
    file_names = sliced_dataset[dataset_key]['files']
    print(f"Name: {list(file_names.keys())[0]}")
    print(f"-------------------------------------------")
    file_path = list(file_names.keys())[0]

    file_name = os.path.basename(file_path)
    root_file = os.path.splitext(file_name)[0]

    dataset_key = list(sliced_dataset.keys())[0]
    datatype = sliced_dataset[dataset_key]["metadata"]["datatype"]

    if datatype == "mc":
        genEventSumw, unskimmed_count = get_genevents_from_coffea(file_path)
    elif datatype == "data":
        unskimmed_count = get_data_events(file_path)

    """Process and skim individual files."""
    skimmed_dict = apply_to_fileset(
        make_skimmed_events,
        sliced_dataset,
        schemaclass=NanoAODSchema,
        uproot_options={"handler": uproot.MultithreadedXRootDSource, "timeout": 3600}
#        uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
#        uproot_options={"handler": uproot.MultithreadedXRootDSource, "timeout": 3600}
    )

    for dataset_name, skimmed in skimmed_dict.items():
        total_events = dak.num(skimmed, axis=0).compute()

        print(f"\n### **Skim Performance**")
        print(f"-------------------------------------------")
        print(f"**Unskimmed events:** {unskimmed_count}")
        print(f"**Skimmed events:** {total_events}")
        efficiency = (total_events / unskimmed_count) * 100
        print(f"**Skim efficiency:** {efficiency:.2f}%")
        if datatype == "mc":
            print(f"**genEventSumw:** {genEventSumw}")
#        batch_size = 100000 #50000
#        print(f"**Batch size:** {batch_size}")
        rows = 20000 #20000
        print(f"**Rows per partition:** {rows}")

        conv = uproot_writeable(skimmed)
        if datatype == "mc":
           conv = ak.with_field(conv, genEventSumw, 'genEventSumw')

        uproot.dask_write(
            conv.repartition(rows_per_partition=rows),
            compute=True,
            destination=f"scripts/skims/{run}/{era}/{dataset}",
            prefix=f"{dataset}_{era}_skim{file_index-1}",
            tree_name="Events"
        )
        del conv
        gc.collect()

#        for start in range(0, total_events, batch_size):
#            batch = skimmed[start: start + batch_size]
#            conv = uproot_writeable(batch)
    #        conv = uproot_writeable(skimmed)
#            if datatype == "mc":
#                conv = ak.with_field(conv, genEventSumw, 'genEventSumw')

#            uproot.dask_write(
#                conv.repartition(rows_per_partition=rows),
#                compute=True, 
#                destination=f"scripts/skims/{run}/{era}/{dataset}", 
#                prefix=f"{dataset}_{era}_skim{file_index-1}_batch{start//batch_size}", 
#                tree_name="Events"
#            )
#            del batch, conv
#            gc.collect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process dataset and run.')
    parser.add_argument("era", type=str, choices=["Run2Autumn18", "RunIISummer20UL18NanoAODv9", "Run2018A", "Run2018B", "Run2018C", "Run2018D", "Run3Summer22", "Run3Summer22EE", "Run3Summer23", "Run3Summer23BPix"], help="Era (e.g. RunIISummer20UL18NanoAODv9)")
    parser.add_argument('process', type=str, choices=["DYJets", "TTbar", "tW", "WJets", "TTbarSemileptonic", "SingleTop", "TTX", "Diboson", "Triboson", "SingleMuon", "EGamma", "Run2022C_SingleMuon", "Run2022C_EGamma", "Run2022D_Muon", "Run2022D_EGamma"],  help='Physics group to process (e.g. DYJets)')
    parser.add_argument('dataset', type=str, help='Dataset to process (e.g. TTTo2L2Nu')
    parser.add_argument('--start', type=int, default=1, help='File number at which to start')
    args = parser.parse_args()

    t0 = time.monotonic()

    if "18" in args.era:
        run = "RunII"
    elif "Run3" in args.era:
        run = "Run3"
        year = "2022"

    json_file_path = f'data/jsons/{run}/{year}/{args.era}/{args.era}_{args.process}_preprocessed.json'
    with open(json_file_path, 'r') as file:
        fileset = json.load(file)

    full_dataset = filter_json_by_primary_ds_name(fileset, args.dataset)
#    full_dataset = extract_data(fileset, args.dataset, args.era)
    dataset_key = list(full_dataset.keys())[0]
    num_files = len(full_dataset[dataset_key]['files'])

    sliced_dataset = slice_files(full_dataset, slice(args.start - 1, args.start))

    print('sliced_dataset', sliced_dataset)
    print(f"\n### **Processing Information**")
    print(f"-------------------------------------------")
    print(f"**File:** {args.start} of {num_files}")

    task = process_file(sliced_dataset, dataset_key, args.dataset, args.start, args.era, run)

    exec_time = time.monotonic() - t0
    print(f"**Execution time:** {exec_time/60:.2f} minutes")
    print(f"-------------------------------------------\n")
