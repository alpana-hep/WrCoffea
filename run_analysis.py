import argparse
import time
import json
import utils
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess, max_files
from analyzer import WrAnalysis
from dask.distributed import Client, LocalCluster, progress
from dask.diagnostics import ProgressBar
import dask
import warnings
import gzip
import uproot
import hist.dask as dah
import hist
NanoAODSchema.warn_missing_crossrefs = False
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")

def load_output_json(year, sample):
    if sample != "Signal":
        json_file_path = f'datasets/{year}/{year}ULbkg_available.json.gz'
        with gzip.open(json_file_path, 'rt') as file:
            data = json.load(file)
    else:
        json_file_path = f'datasets/{year}/{year}_Signal.json'
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    return data

def filter_by_process(fileset, desired_process):
    if desired_process == "allBkg" or desired_process == "Signal":
        return fileset
    else:
        filtered_fileset = {}
        for dataset, data in fileset.items():
            if data['metadata']['process'] == desired_process:
                filtered_fileset[dataset] = data
        return filtered_fileset

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Processing script for WR analysis.")
    parser.add_argument("year", type=str, choices=["2016", "2017", "2018"], help="Year to analyze.")
    parser.add_argument("sample", type=str, choices=["DYJets", "tt+tW", "tt_semileptonic", "WJets", "Diboson", "Triboson", "ttX", "SingleTop", "Signal", "allBkg"], help="MC sample to analyze.")
    parser.add_argument("--max_files", type=int, default=None, help="Number of files to analyze.")
    parser.add_argument("--executor", type=str, choices=["local", "lpc"], default=None, help="How to run the processing")
    parser.add_argument("--hists", type=str, help="Get a root file of histograms.")
    parser.add_argument("--masses", type=str, help="Get a root file of mass tuples.")
    args = parser.parse_args()

    if args.year != "2018" and args.sample != "Signal":
        raise NotImplementedError

    t0 = time.monotonic()

    fileset = max_files(filter_by_process(load_output_json(args.year, args.sample), args.sample), args.max_files)

    if args.executor == "local":
#        cluster = LocalCluster(n_workers=8,threads_per_worker=1,memory_limit='1.43GB')
#        cluster = LocalCluster(n_workers=4,threads_per_worker=2,memory_limit='2.84GB')
#        cluster = LocalCluster(n_workers=2,threads_per_worker=4,memory_limit='5.71GB')
        cluster = LocalCluster(n_workers=1,threads_per_worker=8,memory_limit='11.43GB')
        client = Client(cluster)
        print(f"\nStarting a Local Cluster: {client.dashboard_link}")
    elif args.executor == "lpc":
        from lpcjobqueue import LPCCondorCluster
        cluster = LPCCondorCluster(cores=1, memory='8GB',log_directory='/uscms/home/bjackson/logs')
        cluster.scale(200)
        client = Client(cluster)
        print(f"\nStarting an LPC Cluster: http://127.0.0.1:8787/status")
    else:
        print(f"\nNot starting a cluster.")
        client = None

    if args.sample == "Signal":
        fileset, dataset_updated = preprocess(
            fileset=fileset,
            step_size=50_000,
            align_clusters=True,
            recalculate_steps=True,
            files_per_batch = 1,
            skip_bad_files=True,
            scheduler=client,
        )

    print(f"\nStarting to analyze {args.year} {args.sample} files")
    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(),
        fileset=max_chunks(fileset, 300),
        schemaclass=NanoAODSchema,
#        uproot_options={"timeout": 3600},
        uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
    )

    if args.hists:
        utils.hists_output.save_histograms(to_compute, args.hists, client, args.executor)

    if args.masses:
        utils.masses_output.save_tuples(to_compute, args.masses, client)
    if not args.hists and not args.masses:
        print("\nNot saving any histograms or tuples.")

    if args.executor:
        client.close()
        cluster.close()

    exec_time = time.monotonic() - t0
    print(f"\nExecution took {exec_time/60:.2f} minutes\n")
