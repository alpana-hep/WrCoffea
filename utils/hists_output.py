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

    with uproot.recreate(output_file) as root_file:
        for key, hist in my_split_hists.items():
            name, process, channel, mll = key
            path = f'UL18/{process}/{channel}/{mll}/{name}'
            root_file[path] = hist

    print(f"Histograms saved to {output_file}.")

def compute_hists(histos):
    print("\nComputing histograms...")
    with ProgressBar():
        (histograms,)= dask.compute(histos)
    return histograms

def sum_hists(my_hists):
    summed_hists = create_histos()
    for dataset_info in my_hists.values():
        for hist_name, hist_data in dataset_info['hists'].items():
            if hist_name in summed_hists:
                summed_hists[hist_name] += hist_data
            else:
                print(f"Warning: Histogram {hist_name} not found in the template histograms.")

    return summed_hists

def split_hists(summed_hists):
    split_histograms = {}

    for hist_name, sum_hist in summed_hists.items():
        process_axis = sum_hist.axes['process']
        channels_axis = sum_hist.axes['channel']
        mll_axis = sum_hist.axes['mll']

        unique_processes = [process_axis.value(i) for i in range(process_axis.size)]
        unique_channels = [channels_axis.value(i) for i in range(channels_axis.size)]
        unique_mll_ranges = [mll_axis.value(i) for i in range(mll_axis.size)]

        for process in unique_processes:
            for channel in unique_channels:
                for mll in unique_mll_ranges:
                    sub_hist = sum_hist[{process_axis.name: process, channels_axis.name: channel, mll_axis.name: mll}]
                    key = (hist_name, process, channel, mll)
                    split_histograms[key] = sub_hist

    return split_histograms

def create_histos():
    pt_leadlep_axis = hist.axis.Regular(400, 0, 2000, name="pt_leadlep", label=r"p_{T} of the leading lepton [GeV]")
    pt_subleadlep_axis = hist.axis.Regular(400, 0, 2000, name="pt_subleadlep", label=r"p_{T} of the subleading lepton [GeV]")
    pt_leadjet_axis = hist.axis.Regular(400, 0, 2000, name="pt_leadjet", label=r"p_{T} of the leading jet [GeV]")
    pt_subleadjet_axis = hist.axis.Regular(400, 0, 2000, name="pt_subleadjet", label=r"p_{T} of the subleading jet [GeV]")
    pt_dileptons_axis = hist.axis.Regular(200, 0, 1000, name="pt_dileptons", label=r"p^{T}_{ll} [GeV]")

    eta_leadlep_axis = hist.axis.Regular(600, -3, 3, name="eta_leadlep", label=r"#eta of the leading lepton")
    eta_subleadlep_axis = hist.axis.Regular(600, -3, 3, name="eta_subleadlep", label=r"#eta of the subleading lepton")
    eta_leadjet_axis = hist.axis.Regular(600, -3, 3, name="eta_leadjet", label=r"#eta of the leading jet")
    eta_subleadjet_axis = hist.axis.Regular(600, -3, 3, name="eta_subleadjet", label=r"#eta of the subleading jet")

    phi_leadlep_axis = hist.axis.Regular(800, -4, 4, name="phi_leadlep", label=r"#phi of the leading lepton")
    phi_subleadlep_axis = hist.axis.Regular(800, -4, 4, name="phi_subleadlep", label=r"#phi of the subleading lepton")
    phi_leadjet_axis = hist.axis.Regular(800, -4, 4, name="phi_leadjet", label=r"#phi of the leading jet")
    phi_subleadjet_axis = hist.axis.Regular(800, -4, 4, name="phi_subleadjet", label=r"#phi of the subleading jet")

    mass_dileptons_axis = hist.axis.Regular(1000, 0, 5000, name="mass_dileptons", label=r"m_{ll} [GeV]")
    mass_dijets_axis = hist.axis.Regular(1000, 0, 5000, name="mass_dijets", label=r"m_{jj} [GeV]")
    mass_fourobject_axis = hist.axis.Regular(1600, 0, 8000, name="mass_fourobject", label=r"m_{lljj} [GeV]")

    process_axis = hist.axis.StrCategory([], name="process", label="Process", growth=True)
    channel_axis = hist.axis.StrCategory([], name="channel", label="Channel", growth=True)
    mll_axis = hist.axis.StrCategory([], name="mll", label="Dilepton Mass", growth=True)

    hist_dict = {
        "pt_leadlep_h": hist.Hist(pt_leadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_subleadlep_h": hist.Hist(pt_subleadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_leadjet_h": hist.Hist(pt_leadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_subleadjet_h": hist.Hist(pt_subleadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_dileptons_h": hist.Hist(pt_dileptons_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_leadlep_h": hist.Hist(eta_leadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_subleadlep_h": hist.Hist(eta_subleadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_leadjet_h": hist.Hist(eta_leadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_subleadjet_h": hist.Hist(eta_subleadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_leadlep_h": hist.Hist(phi_leadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_subleadlep_h": hist.Hist(phi_subleadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_leadjet_h": hist.Hist(phi_leadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_subleadjet_h": hist.Hist(phi_subleadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "mass_dileptons_h": hist.Hist(mass_dileptons_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "mass_dijets_h": hist.Hist(mass_dijets_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "mass_fourobject_h": hist.Hist(mass_fourobject_axis, process_axis, channel_axis, mll_axis, storage="weight"),
    }

    return hist_dict
