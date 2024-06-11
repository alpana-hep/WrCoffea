import uproot
import os
import dask
from dask.diagnostics import ProgressBar
import hist
from hist import Hist

def save_histograms(all_histograms, hists_name):
    output_dir = "root_outputs/hists/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{hists_name}")

    histograms = compute_hists(all_histograms)

    summed_hist = sum_hists(histograms)

    my_split_hists = split_hists(summed_hist)

    for dataset_path, dataset_info in all_histograms.items():
        mc = dataset_info['mc']
        process = dataset_info['process']
        path = f"{mc}/{process}"
        break

    with uproot.recreate(output_file) as root_file:
        for key, hist in my_split_hists.items():
            channel, mll = key
            path = f'{mc}/{process}/{channel}/{mll}/pT_lead_lepton'
            root_file[path] = hist

    print(f"Histograms saved to {output_file}.")

def compute_hists(histos):
#    print(f"\nhistos {histos}\n")

    print("\nComputing histograms...")
    with ProgressBar():
        (histograms,)= dask.compute(histos)

    print(f"\nComputed histograms: {histograms}\n")
    return histograms

def sum_hists(my_hists):
    summed_hist = (
        Hist.new.Reg(400, 0, 2000, name="pT_lead_lepton", label=r"p_{T} of the leading lepton [GeV]")
        .StrCat([], name="process", label="Process", growth=True)
        .StrCat([], name="channel", label="Channel", growth=True)
        .StrCat([], name="mll", label="Dilepton Mass", growth=True)
        .Weight()
        )

    for dataset_info in my_hists.values():
#        print(f"\nDataset_info: {dataset_info}\n")
        leadlepton_pt_hist = dataset_info['hists']['leadlepton_pt']
        summed_hist += leadlepton_pt_hist

    print(f"Summed hists: {summed_hist}\n")

    summed_hist = summed_hist[:, sum, :, :]
    print(f"Sliced hists: {summed_hist}\n")
    return summed_hist

def split_hists(sum_hists):
    channels = ['eejj', 'mumujj', 'emujj']
    mll_ranges = ['60mll150', '150mll400', '400mll']

    # Create a dictionary to hold the sub-histograms
    sub_histograms = {}

    # Loop through each combination of 'channel' and 'mll'
    for channel in channels:
        for mll in mll_ranges:
            # Project the original histogram to the sub-histogram
            sub_hist = sum_hists[{sum_hists.axes[1].name: channel, sum_hists.axes[2].name: mll}]
            # Store the sub-histogram in the dictionary
            sub_histograms[(channel, mll)] = sub_hist

    print(f"Sub histograms: {sub_histograms}\n")

    return sub_histograms 

