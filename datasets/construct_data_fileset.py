import argparse
from coffea.dataset_tools import rucio_utils
from coffea.dataset_tools.dataset_query import print_dataset_query
from rich.console import Console
from rich.table import Table
from coffea.dataset_tools.dataset_query import DataDiscoveryCLI

dataset_2018 = {
    "/SingleMuon/Run2018A-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD": {"mc_campaign": "UL2018", "process": "SingleMuon", "dataset": "Run2018A"},
    "/SingleMuon/Run2018B-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD": {"mc_campaign": "UL2018", "process": "SingleMuon", "dataset": "Run2018B"},
    "/SingleMuon/Run2018C-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD": {"mc_campaign": "UL2018", "process": "SingleMuon", "dataset": "Run2018C"},
    "/SingleMuon/Run2018D-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL2018", "process": "SingleMuon", "dataset": "Run2018D"},
    "/EGamma/Run2018A-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL2018", "process": "EGamma", "dataset": "Run2018A"},
    "/EGamma/Run2018B-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL2018", "process": "EGamma", "dataset": "Run2018B"},
    "/EGamma/Run2018C-UL2018_MiniAODv2_NanoAODv9-v1/NANOAOD": {"mc_campaign": "UL2018", "process": "EGamma", "dataset": "Run2018C"},
    "/EGamma/Run2018D-UL2018_MiniAODv2_NanoAODv9-v3/NANOAOD": {"mc_campaign": "UL2018", "process": "EGamma", "dataset": "Run2018D"},
}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Construct fileset from list of datasets.')
    parser.add_argument('year', choices=['2018', '2017', '2016'], help='Choose the year to query.')
    args = parser.parse_args()

    if args.year != '2018':
        raise NotImplementedError

    ddc = DataDiscoveryCLI()
    ddc.do_allowlist_sites(["T1_US_FNAL_Disk", "T2_US_Wisconsin", "T2_CH_CERN", "T2_KR_KISTI", "T2_FI_HIP"])
#    ddc.do_allowlist_sites(["T2_DE_DESY", "T2_US_Wisconsin", "T2_US_Nebraska"])
    
    if args.year == '2018':
        ddc.load_dataset_definition(dataset_2018, query_results_strategy="all",replicas_strategy="round-robin")

    ddc.do_save(f"data/UL{args.year}_Data.json") #Use this to do manual preprocessing instead
