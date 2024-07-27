import argparse
import time
import json
import utils
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess, max_files
from analyzer import WrAnalysis
from dask.distributed import Client, LocalCluster
import warnings
import gzip
import uproot

NanoAODSchema.warn_missing_crossrefs = False
warnings.filterwarnings("ignore", category=FutureWarning, module="htcondor")

def load_output_json(year, sample):
    if sample == "Signal":
        json_file_path = f'datasets/signal{year}.json'
        with open(json_file_path, 'r') as file:
            data = json.load(file)
    elif sample == "Data":
        json_file_path = f'datasets/2018Data_available.json.gz'
        with gzip.open(json_file_path, 'rt') as file:
            data = json.load(file)
    else:
        json_file_path = f'datasets/{year}ULbkg_available.json.gz'
        with gzip.open(json_file_path, 'rt') as file:
            data = json.load(file)
    return data

def filter_by_process(fileset, desired_process, mass=None):
    if desired_process == "Signal":
        filtered_fileset = {}
        for dataset, data in fileset.items():
            if data['metadata']['dataset'] == mass:
                filtered_fileset[dataset] = data
    elif desired_process == "Data":
        filtered_fileset = fileset
    else:
        filtered_fileset = {}
        for dataset, data in fileset.items():
            if data['metadata']['process'] == desired_process:
                filtered_fileset[dataset] = data
    return filtered_fileset

if __name__ == "__main__":
    # DYJets:          67/31 minutes for  87,026,512 events.
    # tt+tW:           99/26 minutes for  163,835,543 events.
    # tt_semileptonic: 188.94/28 minutes for 463,092,000 events.
    # WJets:           24.36 minutes for  206,103,400 events.
    # Diboson:         37.80 minutes for  26,032,000 events.
    # Triboson:        7.08 minutes  for  1,036,000 events.
    # ttX:             118.26 minutes for 60,480,677 events.
    # SingleTop:      47.85 minutes for  311,533,999 events.
    parser = argparse.ArgumentParser(description="Processing script for WR analysis.")

    parser.add_argument(
            "year", 
            type=str, 
            choices=["2016", "2017", "2018"], 
            help="Year to analyze."
    )
    parser.add_argument(
            "sample", 
            type=str, 
            choices=["DYJets", "tt+tW", "tt_semileptonic", "WJets", "Diboson", "Triboson", "ttX", "SingleTop", "Signal", "Data"], 
            help="MC sample to analyze."
    )
    parser.add_argument(
            "--mass", 
            type=str, 
            default="",
            choices=['MWR600_MN100', 'MWR600_MN200', 'MWR600_MN400', 'MWR600_MN500', 'MWR800_MN100', 'MWR800_MN200', 
                     'MWR800_MN400', 'MWR800_MN600', 'MWR800_MN700', 'MWR1000_MN100', 'MWR1000_MN200', 'MWR1000_MN400', 
                     'MWR1000_MN600', 'MWR1000_MN800', 'MWR1000_MN900', 'MWR1200_MN100', 'MWR1200_MN200', 'MWR1200_MN400', 
                     'MWR1200_MN600', 'MWR1200_MN800', 'MWR1200_MN1000', 'MWR1200_MN1100', 'MWR1400_MN100', 'MWR1400_MN200', 
                     'MWR1400_MN400', 'MWR1400_MN600', 'MWR1400_MN800', 'MWR1400_MN1000', 'MWR1400_MN1200', 'MWR1400_MN1300', 
                     'MWR1600_MN100', 'MWR1600_MN200', 'MWR1600_MN400', 'MWR1600_MN600', 'MWR1600_MN800', 'MWR1600_MN1000', 
                     'MWR1600_MN1200', 'MWR1600_MN1400', 'MWR1600_MN1500', 'MWR1800_MN100', 'MWR1800_MN200', 'MWR1800_MN400', 
                     'MWR1800_MN600', 'MWR1800_MN800', 'MWR1800_MN1000', 'MWR1800_MN1200', 'MWR1800_MN1400', 'MWR1800_MN1600', 
                     'MWR1800_MN1700', 'MWR2000_MN100', 'MWR2000_MN200', 'MWR2000_MN400', 'MWR2000_MN600', 'MWR2000_MN800', 
                     'MWR2000_MN1000', 'MWR2000_MN1200', 'MWR2000_MN1400', 'MWR2000_MN1600', 'MWR2000_MN1800', 'MWR2000_MN1900', 
                     'MWR2200_MN100', 'MWR2200_MN200', 'MWR2200_MN400', 'MWR2200_MN600', 'MWR2200_MN800', 'MWR2200_MN1000', 
                     'MWR2200_MN1200', 'MWR2200_MN1400', 'MWR2200_MN1600', 'MWR2200_MN1800', 'MWR2200_MN2000', 'MWR2200_MN2100', 
                     'MWR2400_MN100', 'MWR2400_MN200', 'MWR2400_MN400', 'MWR2400_MN600', 'MWR2400_MN800', 'MWR2400_MN1000', 
                     'MWR2400_MN1200', 'MWR2400_MN1400', 'MWR2400_MN1600', 'MWR2400_MN1800', 'MWR2400_MN2000', 'MWR2400_MN2200', 
                     'MWR2400_MN2300', 'MWR2600_MN100', 'MWR2600_MN200', 'MWR2600_MN400', 'MWR2600_MN600', 'MWR2600_MN800', 
                     'MWR2600_MN1000', 'MWR2600_MN1200', 'MWR2600_MN1400', 'MWR2600_MN1600', 'MWR2600_MN1800', 'MWR2600_MN2000', 
                     'MWR2600_MN2200', 'MWR2600_MN2400', 'MWR2600_MN2500', 'MWR2800_MN100', 'MWR2800_MN200', 'MWR2800_MN400', 
                     'MWR2800_MN600', 'MWR2800_MN800', 'MWR2800_MN1000', 'MWR2800_MN1200', 'MWR2800_MN1400', 'MWR2800_MN1600', 
                     'MWR2800_MN1800', 'MWR2800_MN2000', 'MWR2800_MN2200', 'MWR2800_MN2400', 'MWR2800_MN2600', 'MWR2800_MN2700', 
                     'MWR3000_MN100', 'MWR3000_MN200', 'MWR3000_MN400', 'MWR3000_MN600', 'MWR3000_MN800', 'MWR3000_MN1000', 
                     'MWR3000_MN1200', 'MWR3000_MN1400', 'MWR3000_MN1600', 'MWR3000_MN1800', 'MWR3000_MN2000', 'MWR3000_MN2200', 
                     'MWR3000_MN2400', 'MWR3000_MN2600', 'MWR3000_MN2800', 'MWR3000_MN2900', 'MWR3200_MN100', 'MWR3200_MN200', 
                     'MWR3200_MN400', 'MWR3200_MN600', 'MWR3200_MN800', 'MWR3200_MN1000', 'MWR3200_MN1200', 'MWR3200_MN1400', 
                     'MWR3200_MN1600', 'MWR3200_MN1800', 'MWR3200_MN2000', 'MWR3200_MN2200', 'MWR3200_MN2400', 'MWR3200_MN2600', 
                     'MWR3200_MN2800', 'MWR3200_MN3000', 'MWR3200_MN3100', 'MWR3400_MN100', 'MWR3400_MN200', 'MWR3400_MN400', 
                     'MWR3400_MN600', 'MWR3400_MN800', 'MWR3400_MN1000', 'MWR3400_MN1200', 'MWR3400_MN1400', 'MWR3400_MN1600', 
                     'MWR3400_MN1800', 'MWR3400_MN2000', 'MWR3400_MN2200', 'MWR3400_MN2400', 'MWR3400_MN2600', 'MWR3400_MN2800', 
                     'MWR3400_MN3000', 'MWR3400_MN3200', 'MWR3400_MN3300'],
            help="Signal mass point to analyze"
    )
    parser.add_argument(
            "--max_files", 
            type=int, 
            default=None, 
            help="Number of files to analyze per dataset"
    )
    parser.add_argument(
            "--executor", 
            type=str, 
            choices=["local", "lpc"], 
            default=None, 
            help="How to run the processing"
    )
    parser.add_argument(
            "--hists", 
            type=str, 
            help="Get a root file of histograms."
    )
    parser.add_argument(
            "--masses", 
            type=str, 
            help="Get a root file of mass tuples."
    )
    args = parser.parse_args()

    if args.year != "2018":
        raise NotImplementedError("Only 2018 samples currently exist.")

    if args.sample == "Signal" and args.mass == "":
        raise ValueError("Enter a signal mass point (e.g. --mass MWR3000_MN1600)")

    if args.sample != "Signal" and args.mass:
        raise ValueError("Sample must be Signal!")

    t0 = time.monotonic()

    if args.executor == "local":
        cluster = LocalCluster(n_workers=1,threads_per_worker=8,memory_limit='11.43GB') #Try (2,4,5.71), (4,2,2.84), (8,1,1.43)
        client = Client(cluster)
#        client = Client()
        print(f"\nStarting a Local Cluster: {client.dashboard_link}")
    elif args.executor == "lpc":
        from lpcjobqueue import LPCCondorCluster
        cluster = LPCCondorCluster(cores=2, memory='8GB',log_directory='/uscms/home/bjackson/logs') #Changed form 8GB to 10GB
        cluster.scale(200)
        client = Client(cluster)
        print(f"\nStarting an LPC Cluster")
    else:
        client = None

    print(f"\nStarting to analyze {args.year} {args.sample} files")

    if args.sample == "Signal":

        fileset = max_files(filter_by_process(load_output_json(args.year, args.sample), args.sample, args.mass), args.max_files)

        fileset, dataset_updated = preprocess(
            fileset=fileset,
            step_size=50_000,
            align_clusters=True,
            recalculate_steps=True,
            files_per_batch = 1,
            skip_bad_files=True,
            scheduler=client,
        )

        to_compute = apply_to_fileset(
            data_manipulation=WrAnalysis(mass_point=args.mass),
            fileset=max_chunks(fileset, 500),
            schemaclass=NanoAODSchema,
            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
        )
        if args.hists:
            utils.save_hists.save_histograms(to_compute, args.hists, client, args.executor, args.sample)
        if args.masses:
            print("to_compute:", to_compute)
            utils.save_masses.save_tuples(to_compute, args.masses, client)
    else:
        fileset = max_files(filter_by_process(load_output_json(args.year, args.sample), args.sample), args.max_files)

        to_compute = apply_to_fileset(
            data_manipulation=WrAnalysis(),
            fileset=max_chunks(fileset, 1000),
            schemaclass=NanoAODSchema,
            uproot_options={"handler": uproot.XRootDSource, "timeout": 3600}
        )
        if args.hists:
            utils.save_hists.save_histograms(to_compute, args.hists, client, args.executor, args.sample)
   
        if args.masses:
            utils.save_masses.save_tuples(to_compute, args.masses, client)

    if not args.hists and not args.masses:
        print("\nNot saving any histograms or tuples.")

    if args.executor:
        client.close()
        cluster.close()

    exec_time = time.monotonic() - t0
    print(f"\nExecution took {exec_time/60:.2f} minutes\n")
