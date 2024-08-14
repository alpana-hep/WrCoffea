import ROOT
import matplotlib.pyplot as plt
import os
import numpy as np
import mplhep as hep
import array
import histogram_configs
import matplotlib.ticker as mticker
import matplotlib.patches as mpatches

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

def plot_histogram(channel, mll, hist_name, hist_dict, signal_hist=None):
    fig, (ax, ax_ratio) = plt.subplots(nrows=2,ncols=1,gridspec_kw={"height_ratios": [5, 1]},figsize=(10, 10))

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
            [other, nonprompt, dy, ttbar],
            stack=True,
            bins=bins,
#            yerr=np.sqrt([other, nonprompt, ttbar, dy]),
            histtype='fill',
            color=['#00BFFF', '#32CD32', '#FFFF00', '#FF0000'],
            alpha=[1, 1, 1, 1],
            edgecolor=["k", "k", "k", "k"],
            label=[
                "Other backgrounds",
                "Nonprompt",
                "Z+jets",
                r"$t\bar{t}+tW$",
            ],
            ax=ax
    )

    hep.cms.label(data=False, lumi=59.74, fontsize=20, ax=ax)

    # Plot the uncertainty on the combined backgrounds

#    circ1 = mpatches.Patch( facecolor='k',alpha=0.6,hatch=r'\\\\',label='Label1')
#    ax.errorbar(
#        bin_centers,
#        combined_sim,
#        yerr=combined_sim_err, 
#        xerr=bin_widths*0.5,
#        marker =circ1
#        markersize=8, 
#        markerfacecolor='blue', 
#        markeredgecolor='black', 
#        markeredgewidth=1.5,
#        capsize=3, 
#        linestyle='none'
#    )
    
    # Plot data histogram if available
    if signal_hist:
        rebinned_signal_hist = signal_hist.Rebin(len(bins)-1, "hnew_data", bins)
        signal_contents = []
        xerrs = []
        signal_errs = []
        center = []
        for bin in range(1, rebinned_signal_hist.GetNbinsX() + 1):
            bin_width = bins[bin] - bins[bin - 1]
            center.append((bins[bin] + bins[bin - 1]) * 0.5)
            xerrs.append(bin_width * 0.5)
            signal_contents.append(rebinned_signal_hist.GetBinContent(bin)* 59.74 * 1000)
            signal_errs.append(rebinned_signal_hist.GetBinError(bin)* 59.74 * 1000)
    
        signal_contents = np.array(signal_contents)

        hep.histplot(
            signal_contents,
            stack=False,
            bins=bins,
#            yerr=signal_errs,
            histtype='step',
            linestyle='dashdot',
            linewidth=2,
            color='black',
            label=r"$(m_{W_R}, m_{N})=(2000,1000) \mathrm{~GeV}$",
            ax=ax
        )

#        ratio = np.divide(signal_contents, combined_sim, where=combined_sim!=0)
#        ratio_err = ratio * np.sqrt(np.square(signal_errs / signal_contents) + np.square(combined_sim_err / combined_sim), where=combined_sim!=0)
        
#        ax_ratio.errorbar(
#            center,
#            ratio,
#            xerr=xerrs,
#            yerr=ratio_err,
#            fmt='o',
#            linewidth=2,
#            capsize=2,
#            color='black',
#        )

        ax_ratio.axhline(1, color='black', linestyle='-')

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

    plt.subplots_adjust(hspace=0.1)

    # Add the text box in the top-left corner
    if channel == "mumujj" and mll == "400mll":
        flavor = r"$\mu\mu$"
        region = "$m_{ll} > 400 \mathrm{~GeV}$"
    elif channel == "eejj" and mll == "400mll":
        flavor = r"$ee$"
        region = "$m_{ll} > 400 \mathrm{~GeV}$"
    elif channel == "emujj":
        flavor = r"$e\mu$"
        region = "Resolved Flavor CR"
    ax.text(0.05, 0.96, flavor, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')
    ax.text(0.05, 0.91, region, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')

    # Create output directory if it doesn't exist
    output_path = os.path.join("plots", channel, mll,  f"{hist_name}.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the plot
    plt.savefig(output_path)
    print(f"Saved {output_path}")
    plt.close()

if __name__ == "__main__":
    input_file = "root_outputs/hists/2018ULbkg_august5/2018ULbkg_aug5.root"
    f_in = ROOT.TFile(input_file, "READ")
    my_histos = get_histograms(f_in)
    sorted_histograms = organize_histograms(my_histos)

    # Load signal file
    signal_file = "root_outputs/hists/2018ULbkg_august5/MWR2000_MN1000.root"
    f_signal = ROOT.TFile(signal_file, "READ")
    signal_histos = get_histograms(f_signal)
    sorted_signal_histograms = organize_histograms(signal_histos)

    for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
        if hist_name == "mass_fourobject" and mll == "400mll":
            grouped_hist_dict = group_histograms(hist_dict)
            reordered_dict = reorder_dict(mll, grouped_hist_dict)
            signal_hist = sorted_signal_histograms.get((channel, mll, hist_name), {}).get("MWR2000_MN1000", None)
            plot_histogram(channel, mll, hist_name, reordered_dict, signal_hist)

    f_in.Close()
    print(f"Finished making histograms.")
