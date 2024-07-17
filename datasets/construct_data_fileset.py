import argparse
from coffea.dataset_tools import rucio_utils
from coffea.dataset_tools.dataset_query import print_dataset_query
from rich.console import Console
from rich.table import Table
from coffea.dataset_tools.dataset_query import DataDiscoveryCLI

dataset_2018 = {
    "/SingleMuon/Run2018A-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "SingleMuon", "dataset": "Run2018A"},
    "/SingleMuon/Run2018B-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "SingleMuon", "dataset": "Run2018B"},
    "/SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "SingleMuon", "dataset": "Run2018C"},
    "/SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "SingleMuon", "dataset": "Run2018D"},
    "/EGamma/Run2018A-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "EGamma", "dataset": "Run2018A"},
    "/EGamma/Run2018B-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "EGamma", "dataset": "Run2018B"},
    "/EGamma/Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "EGamma", "dataset": "Run2018C"},
    "/EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD": {"mc_campaign": "UL18", "lumi": 59.74, "process": "EGamma", "dataset": "Run2018D"},
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Construct fileset from list of datasets.')
    parser.add_argument('year', choices=['2018', '2017', '2016'], help='Choose the year to query.')
    args = parser.parse_args()

    if args.year != '2018':
        raise NotImplementedError

    ddc = DataDiscoveryCLI()
    ddc.do_allowlist_sites(["T2_DE_DESY", "T2_US_Wisconsin", "T2_US_Nebraska"])
    
    if args.year == '2018':
        ddc.load_dataset_definition(dataset_2018, query_results_strategy="all",replicas_strategy="round-robin")

    ddc.do_save(f"UL{args.year}Data.json") #Use this to do manual preprocessing instead

    fileset_total = ddc.do_preprocess(output_file=f'{args.year}Data',
                  step_size=70000,
                  align_to_clusters=False,
                  scheduler_url=None)
