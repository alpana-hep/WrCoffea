import argparse
import time

from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess, max_files

import utils
from analyzer import WrAnalysis

import dask
from dask.distributed import Client, LocalCluster
from dask.diagnostics import ProgressBar

import json

NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here

def main(sample, files_max, output_file):

    print("Starting analyzer...\n")
    t0 = time.monotonic()

    #Construct the fileset to pass to preprocess
    fileset = max_files(load_output_json(sample), files_max)
#    print(f"fileset: {fileset}\n")

    #Preprocess files
    dataset_runnable, dataset_updated = preprocess(
            fileset=fileset, 
            step_size=10_000,
            align_clusters=True,
            recalculate_steps=False, 
            files_per_batch = 1, 
            skip_bad_files=True,
            save_form=False,
            scheduler=None,
            uproot_options={"timeout": 10000},
            step_size_safety_factor = 0.5)
#    print(f"dataset_runnable: {dataset_runnable}\n")

    #Process files
    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(),
        fileset=max_chunks(dataset_runnable,1),
        schemaclass=NanoAODSchema,
        uproot_options = {"timeout": 10000})
#    print(f"\nto_compute: {to_compute}")

    #Get histograms
#    print("\nComputing histograms...")
#    with ProgressBar():
#        (all_histograms,) = dask.compute(to_compute) 
#    print("Histograms computed.\n")
#    print(f"{all_histograms}\n")

    utils.file_output.save_histograms(to_compute, output_file)

    exec_time = time.monotonic() - t0
    print(f"Execution took {exec_time/60:.2f} minutes")

def load_output_json(sample):
    json_file_path = f'datasets/filesets/{sample}.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the analyzer and save histograms to a specified ROOT file.")
    parser.add_argument("sample", type=str, choices=["UL18_bkg", "UL17_bkg", "UL16_bkg"], help="Sample to analyze.")
    parser.add_argument("--files_max", type=int, default=None, help="Number of files to analyze.")
    parser.add_argument("--output_file", type=str, default="example_hists.root", help="Name of the output ROOT histogram file.")
    args = parser.parse_args()

    main(args.sample, args.files_max, args.output_file)
