import ROOT
import matplotlib.pyplot as plt
import os
import numpy as np
import mplhep as hep
import array
import histogram_configs
import matplotlib.ticker as mticker

hep.style.use("CMS")

# Function to recursively get histograms from a directory in a ROOT file
def get_histograms(directory, path=""):
    histograms = {}
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        obj_path = os.path.join(path, obj.GetName())
        if obj.IsA().InheritsFrom("TDirectory"):
            histograms.update(get_histograms(obj, obj_path))
        elif obj.IsA().InheritsFrom("TH1"):
            histograms[obj_path] = obj
    return histograms

def organize_histograms(histograms):
    organized_histograms = {}
    for path, hist in histograms.items():
        components = path.split(os.sep)

        process = components[0]
        channel = components[1]
        mll = components[2]
        hist_name = components[3]

        key = (channel, mll, hist_name)

        if key not in organized_histograms:
            organized_histograms[key] = {}
        organized_histograms[key][process] = hist

    return organized_histograms

def group_histograms(hist_dict):
    stacked_histograms = {}
        
    groupings = {
        'Z+jets': ['DYJets'],
        'tt+tW': ['tt+tW'],
        'Nonprompt': ['tt_semileptonic', 'WJets', 'SingleTop'],
        'Other Backgrounds': ['ttX', 'Diboson', 'Triboson']
    }

    for group_name, processes in groupings.items():
        stacked_histogram = None
        for process in processes:
            if process in hist_dict:
                hist = hist_dict[process]
                if stacked_histogram is None:
                    stacked_histogram = hist.Clone()
                else:
                    stacked_histogram.Add(hist)
        if stacked_histogram is not None:
            stacked_histograms[group_name] = stacked_histogram
    return stacked_histograms

def reorder_dict(mll, original_dict):
    if mll == "60mll150":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'tt+tW', 'Z+jets']
    elif mll == "150mll400":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'tt+tW', 'Z+jets']
    elif mll == "150mll":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'tt+tW', 'Z+jets']
    elif mll == "400mll":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'Z+jets', 'tt+tW']
    else:
        return original_dict
    reordered_dict = {key: original_dict[key] for key in desired_order}

    return reordered_dict

def plot_histogram(channel, mll, hist_name, hist_dict, data_hist=None):
    if data_hist:
        fig, (ax, ax_ratio) = plt.subplots(nrows=2,ncols=1,gridspec_kw={"height_ratios": [5, 1]},figsize=(10, 10))
    else:
        fig, ax = plt.subplots(figsize=(10, 10))

    # Set the bins, labels and limits based on the hist_name and mll
    if hist_name in histogram_configs.configurations:
        xlabel = histogram_configs.configurations[hist_name]["xlabel"]
        if mll in histogram_configs.configurations[hist_name]:
            config = histogram_configs.configurations[hist_name][mll]
            bins = np.array(array.array('d', config["bins"]))
            ylabel = config["ylabel"]
            xlim = config["xlim"]
            ylim = config["ylim"]

    dy = []
    dy_err = []
    ttbar = []
    ttbar_err = []
    nonprompt = []
    nonprompt_err = []
    other = []
    other_err = []

    for process, hist in hist_dict.items():
        bin_centers, bin_widths = [], []
        rebinned_hist = hist.Rebin(len(bins)-1, "hnew", bins)
        for bin in range(1, rebinned_hist.GetNbinsX() + 1):
            bin_centers.append(rebinned_hist.GetBinCenter(bin))
            bin_widths.append(rebinned_hist.GetBinWidth(bin))
            if process == 'Z+jets':
                dy.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)
                dy_err.append(rebinned_hist.GetBinError(bin) * 59.74 * 1000)
            elif process == 'tt+tW':
                ttbar.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)
                ttbar_err.append(rebinned_hist.GetBinError(bin) * 59.74 * 1000)
            elif process == 'Nonprompt':
                nonprompt.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)
                nonprompt_err.append(rebinned_hist.GetBinError(bin) * 59.74 * 1000)
            elif process == 'Other Backgrounds':
                other.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)
                other_err.append(rebinned_hist.GetBinError(bin) * 59.74 * 1000)

    # Convert lists to numpy arrays
    dy = np.array(dy)
    dy_err = np.array(dy_err)
    ttbar = np.array(ttbar)
    ttbar_err = np.array(ttbar_err)
    nonprompt = np.array(nonprompt)
    nonprompt_err = np.array(nonprompt_err)
    other = np.array(other)
    other_err = np.array(other_err)

    bin_centers, bin_widths = np.array(bin_centers), np.array(bin_widths)

    combined_sim = dy + ttbar + nonprompt + other
    combined_sim_err = np.sqrt(dy_err**2 + ttbar_err**2 + nonprompt_err**2 + other_err**2)

    # Plot stacked histogram
    hep.histplot(
            [other, nonprompt, ttbar, dy],
            stack=True,
            bins=bins,
            histtype='fill',
            color=['#00BFFF', '#32CD32', '#FF0000', '#FFFF00'],
            alpha=[1, 1, 1, 1],
            edgecolor=["k", "k", "k", "k"],
            label=[
                "Other backgrounds",
                "Nonprompt",
                r"$t\bar{t}+tW$",
                "Z+jets",
            ],
            ax=ax
    )

    hep.cms.label(data=True,lumi=59.74, fontsize=20, ax=ax)

    ax.set_ylabel(ylabel)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_yscale('log')
    ax.legend(reverse=True, fontsize=20)

    def custom_log_formatter(y, pos):
        if y == 1:
            return '1'
        elif y == 10:
            return '10'
        else:
            return f"$10^{{{int(np.log10(y))}}}$"

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(custom_log_formatter))

    # Plot data histogram if available
    if data_hist:
        rebinned_data_hist = data_hist.Rebin(len(bins)-1, "hnew_data", bins)
        data_contents = []
        data_errs = []
        for bin in range(1, rebinned_data_hist.GetNbinsX() + 1):
            data_contents.append(rebinned_data_hist.GetBinContent(bin))
            data_errs.append(rebinned_data_hist.GetBinError(bin))

        data_contents, data_errs = np.array(data_contents), np.array(data_errs)

        ax.errorbar(
            bin_centers,
            data_contents,
            xerr=bin_widths*0.5,
            yerr=data_errs,
            fmt='o',
            linewidth=2, 
            capsize=2,
            color='black',
            label='Data',
        )


        # Create the ratio plot
        ratio = np.divide(data_contents, combined_sim, out=np.zeros_like(data_contents), where=combined_sim!=0)

        # Calculate the ratio errors with handling for division by zero or NaN
        data_fraction = np.divide(data_errs, data_contents, out=np.zeros_like(data_errs), where=data_contents!=0)
        sim_fraction = np.divide(combined_sim_err, combined_sim, out=np.zeros_like(combined_sim_err), where=combined_sim!=0)

        ratio_errors = ratio * np.sqrt(data_fraction**2 + sim_fraction**2)

        ax_ratio.errorbar(
            bin_centers,
            ratio,
            xerr=bin_widths*0.5,
            yerr=ratio_errors,
            fmt='o',
            linewidth=2,
            capsize=2,
            color='black',
        )

        ax_ratio.axhline(1, color='black', linestyle='--')

        ax.set_xticklabels([])

        ax_ratio.set_xlabel(xlabel)
        ax_ratio.set_ylabel(r"$\frac{Data}{Sim.}$")
        ax_ratio.set_ylim(0.7, 1.3)
        ax_ratio.set_yticks([0.8, 1.0, 1.2])
        ax_ratio.set_xlim(xlim)

        plt.subplots_adjust(hspace=0.1)
    else:
        ax.set_xlabel(xlabel)

    # Add the text box in the top-left corner
    if channel == "mumujj":
        flavor = r"$\mu\mu$"
        if mll == "60mll150":
            region = "$60 < m_{ll} < 150 \mathrm{~GeV}$"
        elif mll == "150mll":
            region = "$m_{ll} > 150 \mathrm{~GeV}$"
        elif mll == "150mll400":
            region = "$150 < m_{ll} < 400 \mathrm{~GeV}$"
        elif mll == "400mll":
            region = "$m_{ll} > 400 \mathrm{~GeV}$"
    if channel == "eejj":
        flavor = r"$\mu\mu$"
        if mll == "60mll150":
            region = "$60 < m_{ll} < 150 \mathrm{~GeV}$"
        elif mll == "150mll":
            region = "$m_{ll} > 150 \mathrm{~GeV}$"
        elif mll == "150mll400":
            region = "$150 < m_{ll} < 400 \mathrm{~GeV}$"
        elif mll == "400mll":
            region = "$m_{ll} > 400 \mathrm{~GeV}$"
    elif channel == "emujj":
        flavor = r"$e\mu$"
        if mll == "60mll150":
            region = "$60 < m_{ll} < 150 \mathrm{~GeV}$"
        elif mll == "150mll":
            region = "$m_{ll} > 150 \mathrm{~GeV}$"
        elif mll == "150mll400":
            region = "$150 < m_{ll} < 400 \mathrm{~GeV}$"
        elif mll == "400mll":
            region = "$m_{ll} > 400 \mathrm{~GeV}$"
    ax.text(0.05, 0.96, flavor, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')
    ax.text(0.05, 0.91, region, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')

    # Create output directory if it doesn't exist
    output_path = os.path.join("plots", channel, mll,  f"{hist_name}_0815.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the plot
    plt.savefig(output_path)
    print(f"Saved {output_path}")
    plt.close()

if __name__ == "__main__":
    input_file = "root_outputs/hists/mll_optimization_0815/all_bkgs.root"
    f_in = ROOT.TFile(input_file, "READ")
    my_histos = get_histograms(f_in)
    sorted_histograms = organize_histograms(my_histos)

    # Load data file
    data_file = "root_outputs/hists/mll_optimization_0815/Data.root"
    f_data = ROOT.TFile(data_file, "READ")
    data_histos = get_histograms(f_data)
    sorted_data_histograms = organize_histograms(data_histos)

    for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
        if hist_name != "mass_dileptons_fourobject":
            grouped_hist_dict = group_histograms(hist_dict)
            reordered_dict = reorder_dict(mll, grouped_hist_dict)
            data_hist = sorted_data_histograms.get((channel, mll, hist_name), {}).get("SingleMuon", None)
            plot_histogram(channel, mll, hist_name, reordered_dict, data_hist)

    f_in.Close()
    print(f"Finished making histograms.")
