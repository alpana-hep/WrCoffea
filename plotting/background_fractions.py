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

    fig, (ax, ax_ratio) = plt.subplots(nrows=2,ncols=1,gridspec_kw={"height_ratios": [5, 1]},figsize=(10, 10))

    # Set the bins, labels and limits based on the hist_name and mll
    if hist_name in histogram_configs.configurations:
        xlabel = histogram_configs.configurations[hist_name]["xlabel"]
        xlabel = xlabel.replace("GeV", "TeV")
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
                dy.append(rebinned_hist.GetBinContent(bin))
                dy_err.append(rebinned_hist.GetBinError(bin))
            elif process == 'tt+tW':
                ttbar.append(rebinned_hist.GetBinContent(bin))
                ttbar_err.append(rebinned_hist.GetBinError(bin))
            elif process == 'Nonprompt':
                nonprompt.append(rebinned_hist.GetBinContent(bin))
                nonprompt_err.append(rebinned_hist.GetBinError(bin))
            elif process == 'Other Backgrounds':
                other.append(rebinned_hist.GetBinContent(bin))
                other_err.append(rebinned_hist.GetBinError(bin))

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

    dy_frac = np.divide(dy, combined_sim)
    dy_frac_err = dy_frac * np.sqrt((dy_err/dy)**2 + (combined_sim_err/combined_sim)**2)

    ttbar_frac = np.divide(ttbar, combined_sim)
    ttbar_frac_err = ttbar_frac * np.sqrt((ttbar_err/ttbar)**2 + (combined_sim_err/combined_sim)**2)

    nonprompt_frac = np.divide(nonprompt, combined_sim)
    nonprompt_frac_err = nonprompt_frac * np.sqrt((nonprompt_err/nonprompt)**2 + (combined_sim_err/combined_sim)**2)

    other_frac = np.divide(other, combined_sim)
    other_frac_err = other_frac * np.sqrt((other_err/other)**2 + (combined_sim_err/combined_sim)**2)

    # Main plot
    hep.histplot(
            [other_frac, nonprompt_frac, ttbar_frac, dy_frac],
            bins=bins,
            yerr=[other_frac_err, nonprompt_frac_err, ttbar_frac_err, dy_frac_err],
            stack=False,
            histtype='errorbar',
            xerr=True,
            color=['#9c9ca1', '#964a8b', '#e42536', '#f89c20'], # AN colors are ['#00BFFF', '#32CD32', '#FF0000', '#FFFF00']
            linewidth=2,
            label=[
                "Other backgrounds",
                "Nonprompt",
                r"$t\bar{t}+tW$",
                "Z+jets",
            ],
            ax=ax
    )

    # Format the CMS label
    hep.cms.label(data=False, fontsize=20, ax=ax)

    # Create the ratio and its error
    ratio = np.divide(ttbar_frac, dy_frac)
    ratio_err = ratio * np.sqrt(np.square(ttbar_frac_err / ttbar_frac) + np.square(dy_frac_err / dy_frac))

    # Plot the ratio points
    ax_ratio.errorbar(
            bin_centers,
            ratio,
            yerr=ratio_err,
            xerr=bin_widths*0.5,
            fmt='o',
            linewidth=2,
            capsize=2,
            color='black',
    )

    # Put dashed line across 1 on the ratio plot
    ax_ratio.axhline(1, color='black', linestyle='--')


    # y-axis settings on main plot
    ax.set_ylabel("Background Fraction", fontsize=20)
    ax.set_ylim(0, 1.199)
    ax.yaxis.set_tick_params(labelsize=17)

    # X-axis settings on main plot
    ax.set_xlim(xlim)
    ax.set_xticklabels([])

    # Plot the legend on the main plot
    ax.legend(reverse=True, fontsize=20)

    # Format the y-axis on the ratio plot
    ax_ratio.set_ylabel(r"$\frac{t\bar{t}+tW}{Z+jets}$")
    ax_ratio.set_ylim(0, 2)
    ax_ratio.set_yticks([0, 1, 2])
    ax_ratio.yaxis.set_tick_params(labelsize=17)

    # Format the x-axis on the ratio plot
    ax_ratio.set_xlim(xlim)
    ax_ratio.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}"))
    ax_ratio.set_xlabel(xlabel, fontsize=20)
    ax_ratio.xaxis.set_tick_params(labelsize=17)

    # Adjust the space between the main plot and the ratio plot
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
    output_path = os.path.join("plots", channel, mll,  f"{hist_name}_BKGFRAC.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the plot
    plt.savefig(output_path, dpi=600)
    plt.close()

if __name__ == "__main__":
    input_file = "root_outputs/hists/2018ULbkg_august5/2018ULbkg_aug5.root"
    f_in = ROOT.TFile(input_file, "READ")
    my_histos = get_histograms(f_in)
    sorted_histograms = organize_histograms(my_histos)

    for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
        if hist_name == "mass_fourobject" and mll == "400mll":
            grouped_hist_dict = group_histograms(hist_dict)
            reordered_dict = reorder_dict(mll, grouped_hist_dict)
            plot_histogram(channel, mll, hist_name, reordered_dict)
            print(f"Saved plots/{channel}/{mll}/{hist_name}_BKGFRAC.png")

    f_in.Close()
    print(f"Finished making histograms.")
