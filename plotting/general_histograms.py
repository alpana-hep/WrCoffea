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
    elif mll == "400mll":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'Z+jets', 'tt+tW']
    else:
        return original_dict
    reordered_dict = {key: original_dict[key] for key in desired_order}

    return reordered_dict

def plot_histogram(channel, mll, hist_name, hist_dict, data_hist=None):
    fig, (ax, ax_ratio) = plt.subplots(
        nrows=2,
        ncols=1,
        gridspec_kw={"height_ratios": [5, 1]},
        figsize=(10, 10)
    )

    # Set the bins, labels and limits based on the hist_name and mll
    if hist_name in histogram_configs.configurations:
        xlabel = histogram_configs.configurations[hist_name]["xlabel"]
        if mll in histogram_configs.configurations[hist_name]:
            config = histogram_configs.configurations[hist_name][mll]
            bins = np.array(array.array('d', config["bins"]))
            ylabel = config["ylabel"]
            xlim = config["xlim"]
            ylim = config["ylim"]

    # Initialize variables to hold histogram data
    dy = []
    ttbar = []
    nonprompt = []
    other = []
    for process, hist in hist_dict.items():
        rebinned_hist = hist.Rebin(len(bins)-1, "hnew", bins)
        hist_contents = []
        hist_errors = []
        for bin in range(1, rebinned_hist.GetNbinsX() + 1):
            bin_width = bins[bin] - bins[bin - 1]
            hist_contents.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)
            hist_errors.append(rebinned_hist.GetBinError(bin) * 59.74 * 1000)
        if process == 'Z+jets':
            dy = np.array(hist_contents)
            dy_err = np.array(hist_errors)
        elif process == 'tt+tW':
            ttbar = np.array(hist_contents)
            ttbar_err = np.array(hist_errors)
        elif process == 'Nonprompt':
            nonprompt = np.array(hist_contents)
            nonprompt_err = np.array(hist_errors)
        elif process == 'Other Backgrounds':
            other = np.array(hist_contents)
            other_err = np.array(hist_errors)

    combined_sim = other + nonprompt + ttbar + dy
    combined_errors = np.sqrt(np.square(other_err) + np.square(nonprompt_err) + np.square(ttbar_err) + np.square(dy_err))

    # Plot stacked histogram
    hep.histplot(
            [other, nonprompt, ttbar, dy],
            stack=True,
            bins=bins,
            yerr=np.sqrt([other, nonprompt, ttbar, dy]),
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

    # Plot data histogram if available
    if data_hist:
        rebinned_data_hist = data_hist.Rebin(len(bins)-1, "hnew_data", bins)
        data_contents = []
        xerrs = []
        yerrs = []
        center = []
        for bin in range(1, rebinned_data_hist.GetNbinsX() + 1):
            bin_width = bins[bin] - bins[bin - 1]
            center.append((bins[bin] + bins[bin - 1]) * 0.5)
            xerrs.append(bin_width * 0.5)
            data_contents.append(rebinned_data_hist.GetBinContent(bin))
            yerrs.append(rebinned_data_hist.GetBinError(bin))

        ax.errorbar(
            center,
            data_contents,
            xerr=xerrs,
            yerr=yerrs,
            fmt='o',
            linewidth=2, 
            capsize=2,
            color='black',
            label='Data',
        )

        # Create the ratio plot
        ratio = np.divide(data_contents, combined_sim, out=np.zeros_like(data_contents), where=combined_sim!=0)
        ratio_errors = np.divide(yerrs, combined_sim, out=np.zeros_like(yerrs), where=combined_sim!=0)
        
        ax_ratio.errorbar(
            center,
            ratio,
            xerr=xerrs,
            yerr=ratio_errors,
            fmt='o',
            linewidth=2,
            capsize=2,
            color='black',
        )

        ax_ratio.axhline(1, color='red', linestyle='--')

#    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_ylim(ylim)
    ax.set_xlim(xlim)
    ax.set_yscale('log')
    ax.legend(reverse=True, fontsize=20)

    ax.set_xticklabels([])

    def custom_log_formatter(y, pos):
        if y == 1:
            return '1'
        elif y == 10:
            return '10'
        else:
            return f"$10^{{{int(np.log10(y))}}}$"

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(custom_log_formatter))

    ax_ratio.set_xlabel(xlabel)
    ax_ratio.set_ylabel(r"$\frac{Data}{Sim.}$")
    ax_ratio.set_ylim(0.7, 1.3)
    ax_ratio.set_yticks([0.8, 1.0, 1.2])
    ax_ratio.set_xlim(xlim)

    plt.subplots_adjust(hspace=0.05)

    # Add the text box in the top-left corner
#    ax.text(0.02, 0.98, r"$\mu\mu$", transform=ax.transAxes, fontsize=14,
#            verticalalignment='top', horizontalalignment='left')
#    ax.text(0.02, 0.93, "Resolved DY CR", transform=ax.transAxes, fontsize=14,
#            verticalalignment='top', horizontalalignment='left',
#            bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.5'))


    # Create output directory if it doesn't exist
    output_path = os.path.join("plots", channel, mll,  f"{hist_name}.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the plot
    plt.savefig(output_path)
    plt.close()

if __name__ == "__main__":
    input_file = "root_outputs/hists/2018ULbkg_august5/2018ULbkg_aug5.root"
    f_in = ROOT.TFile(input_file, "READ")
    my_histos = get_histograms(f_in)
    sorted_histograms = organize_histograms(my_histos)

    # Load data file
    data_file = "root_outputs/hists/2018ULbkg_august5/Data.root"
    f_data = ROOT.TFile(data_file, "READ")
    data_histos = get_histograms(f_data)
    sorted_data_histograms = organize_histograms(data_histos)

    for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
        grouped_hist_dict = group_histograms(hist_dict)
        reordered_dict = reorder_dict(mll, grouped_hist_dict)
        data_hist = sorted_data_histograms.get((channel, mll, hist_name), {}).get("SingleMuon", None)
        plot_histogram(channel, mll, hist_name, reordered_dict, data_hist)
        print(f"Saved plots/{channel}/{mll}/{hist_name}.png")

    f_in.Close()
    print(f"Finished making histograms.")
