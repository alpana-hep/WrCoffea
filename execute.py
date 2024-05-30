import argparse
import time

from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess, max_files

import utils
from analyzer import WrAnalysis

import dask
from dask.distributed import Client, LocalCluster
from dask.diagnostics import ProgressBar

NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here

def main(N_FILES_MAX_PER_SAMPLE, output_file):

    print("Starting analyzer...")
    t0 = time.monotonic()

    # Create a local cluster with increased memory limit per worker
#    cluster = LocalCluster(dashboard_address="localhost:8787",memory_limit="auto",n_workers=os.cpu_count(),)
#    client = Client(cluster)
#    print(client)
#    print(cluster.dashboard_link)

    #Construct the fileset to pass to preprocess
    fileset = utils.file_input.construct_fileset(N_FILES_MAX_PER_SAMPLE)

    #Preprocess files (get steps sizes etc)
    filemeta, _ = preprocess(
            fileset=fileset, 
            step_size=1_000,
            align_clusters=True,
            recalculate_steps=False, 
            files_per_batch = 1, 
            skip_bad_files=True,
            save_form=False,
            scheduler=None,
            uproot_options={"timeout": 10000},
            step_size_safety_factor = 0.5)
    
    #Process files
    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(),
        fileset=max_chunks(filemeta,1),
        schemaclass=NanoAODSchema,
        uproot_options = {"timeout": 10000},
    )

#    report=to_compute[1]['2018UL__TTTo2L2Nu']

    #Get histograms
    print("\nComputing histograms...")
    with ProgressBar():
        (all_histograms,) = dask.compute(to_compute['2018UL__TTTo2L2Nu']['hist_dict']) 

    utils.file_output.save_histograms(all_histograms, output_file)

    exec_time = time.monotonic() - t0
    print(f"Execution took {exec_time/60:.2f} minutes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the analyzer and save histograms to a specified ROOT file.")
    parser.add_argument("--nFiles", type=int, default=1, help="Number of files to analyze (-1 for all).")
    parser.add_argument("--outputFile", type=str, default="example_hists.root", help="Name of the output ROOT histogram file.")
    args = parser.parse_args()

    main(args.nFiles, args.outputFile)
