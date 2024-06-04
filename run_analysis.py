import argparse
import time

from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess, max_files

import utils
from analyzer import WrAnalysis

import dask
from dask.distributed import Client, LocalCluster
from dask.diagnostics import ProgressBar
import uproot
import json
import coffea
print("coffea:", coffea.__version__)
print("dask:", dask.__version__)

NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here

def main(sample, hist_out, masses, files_max):

    print("Starting analyzer...\n")
    t0 = time.monotonic()

    #Construct the fileset to pass to preprocess
    fileset = max_files(load_output_json(sample), files_max)
#    print(f"fileset: {fileset}\n")

    #Preprocess files
    dataset_runnable, dataset_updated = preprocess(
            fileset=fileset, 
            step_size=50_000,
            align_clusters=False,
            recalculate_steps=False, 
            files_per_batch = 1, 
            skip_bad_files=True,
            save_form=False,
            scheduler=None,
            step_size_safety_factor = 0.5)
#    print(f"dataset_runnable: {dataset_runnable}\n")

    #Process files
    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(),
        fileset=max_chunks(dataset_runnable,2),
        schemaclass=NanoAODSchema,
    )
#    print(f"\nto_compute: {to_compute}")

    if hist_out:
        utils.hists_output.save_histograms(to_compute, hist_out)
    if masses:
        utils.masses_output.save_tuples(to_compute)
    if not hist_out and not masses:
        print("\nNot saving any histograms or tuples.")

    exec_time = time.monotonic() - t0
    print(f"\nExecution took {exec_time/60:.2f} minutes")

def load_output_json(sample):
    json_file_path = f'datasets/filesets/{sample}.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the analyzer and save histograms to a specified ROOT file.")
    parser.add_argument("sample", type=str, choices=["UL18_bkg", "UL17_bkg", "UL16_bkg"], help="Sample to analyze.")
    parser.add_argument("--output_hists", type=str, help="Get a root file of histograms.")
    parser.add_argument("--output_masses", type=str, help="Get a root file of mass tuples.")
    parser.add_argument("--max_files", type=int, default=None, help="Number of files to analyze.")
    args = parser.parse_args()
    main(args.sample, args.output_hists, args.output_masses, args.max_files,)
