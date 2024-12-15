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

def make_skimmed_events(events, dataset_key):
    """Apply event selection to create skimmed datasets based on a specific branch."""
    # Adjust dataset_key to match the actual format
    base, rest = dataset_key.split("_WR")
    wr, n = rest.split("_N")
    branch_name = f"WRtoNLtoLLJJ_MWR{wr}_MN{n}_TuneCP5_13TeV_madgraph_pythia8"

    # Debugging: Check GenModel and subfields
    if "GenModel" not in events.fields:
        raise ValueError("'GenModel' field not found in the events dataset")
    
    # Check if the branch exists under GenModel
    if branch_name not in events.GenModel.fields:
        raise ValueError(f"Branch '{branch_name}' not found in GenModel subfields")

    # Access the branch under GenModel
    branch_data = events.GenModel[branch_name]
    
    # Debug: Print the type and content of branch_data

    # Convert branch_data to boolean if necessary
    if hasattr(branch_data, "astype"):
        event_filters = branch_data.astype(bool)
    else:
        # Handle case where branch_data is not directly boolean-compatible
        try:
            event_filters = branch_data == True  # Explicit comparison if possible
        except Exception as e:
            raise ValueError(f"Cannot convert branch_data to boolean: {e}")

    # Apply the filter to the events
    skimmed = events[event_filters]

    # Define the fields to keep
    keep_fields = [
        "Electron", "Muon", "Jet", "FatJet", 
        "HLT", "event", "run", "luminosityBlock", 
        "genWeight"
    ]

    # Add the specific branch to the list of fields to keep
#    if branch_name not in keep_fields:
#        keep_fields.append(f"GenModel.{branch_name}")

    # Create skimmed_dropped with selected fields
    skimmed_dropped = skimmed[list(set(x for x in skimmed.fields if x in keep_fields))]

    # Return the filtered events
    return skimmed_dropped

def extract_data(dataset_dict, dataset, config_path="/uscms/home/bjackson/nobackup/WrCoffea/data/configs/Run2Autumn18/Run2Autumn18_sig_cfg_all.json"):
    """Extract data for the given dataset and year from the JSON config."""
    with open(config_path, 'r') as f:
        dataset_mapping = json.load(f)

    found_dataset = None
    for key, details in dataset_mapping.items():
        if details['metadata']['dataset'] == dataset:
            found_dataset = key
            break

    if found_dataset is None:
        raise ValueError(f"Dataset {dataset} not found in the config file")

    return {found_dataset: dataset_dict[found_dataset]}

def process_file(sliced_dataset, dataset_key, dataset, file_index):
    """Process and skim individual files."""
    # Access the list of files for the dataset
    file_names = sliced_dataset[dataset_key]['files']
    # Print the file name being processed
    print(f"Processing files: {file_names.keys()}")
    """Process and skim individual files."""
    skimmed_dict = apply_to_fileset(
        lambda events: make_skimmed_events(events, dataset_key),    
        sliced_dataset,
        schemaclass=NanoAODSchema,
        uproot_options={"handler": uproot.XRootDSource, "timeout": 3600},
    )

    with ProgressBar():
        for dataset_name, skimmed in skimmed_dict.items():
            conv = uproot_writeable(skimmed)
            uproot.dask_write(
                    conv.repartition(rows_per_partition=25000), 
                    compute=True, 
                    destination=f"/uscms/home/bjackson/nobackup/WrCoffea/test/{dataset}", 
                    prefix=f"{dataset}_file{file_index}", 
                    tree_name="Events"
            ) #10000

    gc.collect()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process dataset and run.')
    parser.add_argument('dataset', type=str, help='Dataset to process')
    parser.add_argument('--start', type=int, default=1, help='File number at which to start')
    args = parser.parse_args()

#    client = Client(memory_limit="4GB")
    t0 = time.monotonic()

    json_file_path = f'Run2Autumn18_full_preprocessed.json'
    with open(json_file_path, 'r') as file:
        fileset = json.load(file)

    full_dataset = extract_data(fileset, args.dataset)
    dataset_key = list(full_dataset.keys())[0]
    num_files = len(full_dataset[dataset_key]['files'])

    sliced_dataset = slice_files(full_dataset, slice(args.start - 1, args.start))

    print(f"Skimming file {args.start} of {num_files} for {args.dataset}")
    task = process_file(sliced_dataset, dataset_key, args.dataset, args.start)

    exec_time = time.monotonic() - t0
    print(f"File {args.start} skimmed in {exec_time/60:.2f} minutes.\n")
