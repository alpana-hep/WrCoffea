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

def plot_histogram(channel, mll, hist_name, hist_dict, signal_hists_dict=None):
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

    ###########################################################
    # Calculate the signal and statistical uncertainties      #
    ###########################################################
    if signal_hists_dict:
        mwr1200 = []
        mwr1200_err = []
        mwr2000 = []
        mwr2000_err = []
        mwr3200 = []
        mwr3200_err = []

        for mass_label, signal_hist in signal_hists_dict.items():
            rebinned_signal_hist = signal_hist.Rebin(len(bins)-1, "hnew_data", bins)
            for bin in range(1, rebinned_signal_hist.GetNbinsX() + 1):
                if mass_label == 'MWR1200_MN600':
                    mwr1200.append(rebinned_signal_hist.GetBinContent(bin) * 59.74 * 1000)
                    mwr1200_err.append(rebinned_signal_hist.GetBinError(bin) * 59.74 * 1000)
                elif mass_label == 'MWR2000_MN1000':
                    mwr2000.append(rebinned_signal_hist.GetBinContent(bin) * 59.74 * 1000)
                    mwr2000_err.append(rebinned_signal_hist.GetBinError(bin) * 59.74 * 1000)
                elif mass_label == 'MWR3200_MN1600':
                    mwr3200.append(rebinned_signal_hist.GetBinContent(bin) * 59.74 * 1000)
                    mwr3200_err.append(rebinned_signal_hist.GetBinError(bin) * 59.74 * 1000)

        mwr1200 = np.array(mwr1200)
        mwr1200_err = np.array(mwr1200_err)
        mwr2000 = np.array(mwr2000)
        mwr2000_err = np.array(mwr2000_err)
        mwr3200 = np.array(mwr3200)
        mwr3200_err = np.array(mwr3200_err)

        hep.histplot(
            [mwr1200, mwr2000, mwr3200],
            stack=False,
            bins=bins,
#            yerr=signal_errs,
            histtype='step',
            linestyle='dashed',
            linewidth=2,
            color=['black', '#e76300', '#832db6'],
            label=[
                r"$(m_{W_R}, m_{N})=1200,600 \mathrm{~GeV}$",
                r"$(m_{W_R}, m_{N})=2000,1000 \mathrm{~GeV}$",
                r"$(m_{W_R}, m_{N})=3200,1600 \mathrm{~GeV}$",
            ],
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
    plt.savefig(output_path, dpi=600)
    print(f"Saved {output_path}")
    plt.close()

if __name__ == "__main__":
    bkg_file = "root_outputs/hists/2018ULbkg_august5/2018ULbkg_aug5.root"
    f_bkg_in = ROOT.TFile(bkg_file, "READ")
    my_bkg_histos = get_histograms(f_bkg_in)
    sorted_bkg_histograms = organize_histograms(my_bkg_histos)

    sig_file = "root_outputs/hists/2018ULbkg_august5/Signal_2018.root"
    f_sig_in = ROOT.TFile(sig_file, "READ")
    my_sig_histos = get_histograms(f_sig_in)
    sorted_sig_histograms = organize_histograms(my_sig_histos)

    for (channel, mll, hist_name), hist_dict in sorted_bkg_histograms.items():
        for (sig_channel, sig_mll, sig_hist_name), sig_hist_dict in sorted_sig_histograms.items():
            if (channel, mll, hist_name) == (sig_channel, sig_mll, sig_hist_name):
                if hist_name == "mass_fourobject" and mll == "400mll":
                    grouped_hist_dict = group_histograms(hist_dict)
                    reordered_dict = reorder_dict(mll, grouped_hist_dict)
                    plot_histogram(channel, mll, hist_name, reordered_dict, sig_hist_dict)

    f_bkg_in.Close()
    f_sig_in.Close()
    print(f"Finished making histograms.")

