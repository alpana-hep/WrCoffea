import argparse
import time
import json
import utils
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess, max_files
from analyzer import WrAnalysis
NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here
from dask.distributed import Client, LocalCluster

def main(sample, process, hist_out, masses_out, files_max):

    print("Starting analyzer...\n")
    t0 = time.monotonic()

    fileset = max_files(filter_by_process(load_output_json(sample), process), files_max)

    dataset_runnable, dataset_updated = preprocess(
            fileset=fileset, 
            step_size=10_000,
            align_clusters=False,
            recalculate_steps=True, 
            files_per_batch = 1, 
            skip_bad_files=True,
            save_form=False,
            scheduler=None,
            step_size_safety_factor = 0.5)

    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(),
        fileset=max_chunks(dataset_runnable,1),
        schemaclass=NanoAODSchema,
    )

    if hist_out:
        utils.hists_output.save_histograms(to_compute, hist_out)
    if masses_out:
        utils.masses_output.save_tuples(to_compute, masses_out)
    if not hist_out and not masses_out:
        print("\nNot saving any histograms or tuples.")

    exec_time = time.monotonic() - t0
    print(f"\nExecution took {exec_time/60:.2f} minutes")

def load_output_json(sample):
    json_file_path = f'datasets/{sample}.json'
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    return data

def filter_by_process(fileset, desired_process):
    if desired_process == "allMC":
        return fileset
    else:
        filtered_fileset = {}
        for dataset, data in fileset.items():
            if data['metadata']['process'] == desired_process:
                filtered_fileset[dataset] = data
        return filtered_fileset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the analyzer and save histograms to a specified ROOT file.")
    parser.add_argument("sample", type=str, choices=["UL18_bkg", "UL17_bkg", "UL16_bkg"], help="Sample to analyze.")
    parser.add_argument("process", type=str, choices=["DYJets", "tt+tW", "WJets", "Diboson", "Triboson", "ttX", "SingleTop", "allMC"], help="Process to analyze.")
    parser.add_argument("--hists", type=str, help="Get a root file of histograms.")
    parser.add_argument("--masses", type=str, help="Get a root file of mass tuples.")
    parser.add_argument("--max_files", type=int, default=None, help="Number of files to analyze.")
    args = parser.parse_args()

    cluster = LocalCluster(n_workers=None, threads_per_worker=None, processes=None)
    client = Client(cluster)

    print(f"\nDashboard link is {cluster.dashboard_link}\n")

    main(args.sample, args.process, args.hists, args.masses, args.max_files,)
