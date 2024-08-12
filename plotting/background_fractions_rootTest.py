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

def make_background_fraction(hist_dict):
    print(hist_dict)
    dy = hist_dict['Z+jets']
    ttbar = hist_dict['tt+tW']
    nonprompt = hist_dict['Nonprompt']
    other = hist_dict['Other Backgrounds']

    combined_sim = dy.Clone("combined_sim")
    combined_sim.Add(ttbar)
    combined_sim.Add(nonprompt)
    combined_sim.Add(other)

    print("Combined Simulation Histogram:")
    for i in range(1, combined_sim.GetNbinsX() + 1):
        print(f"Bin {i}: Content = {combined_sim.GetBinContent(i)}, Error = {combined_sim.GetBinError(i)}")

    dy_frac = dy.Clone("dy_frac")
    dy_frac.Divide(combined_sim)

    ttbar_frac = ttbar.Clone("ttbar_frac")
    ttbar_frac.Divide(combined_sim)

    nonprompt_frac = nonprompt.Clone("nonprompt_frac")
    nonprompt_frac.Divide(combined_sim)

    other_frac = other.Clone("other_frac")
    other_frac.Divide(combined_sim)
    
    return dy_frac, ttbar_frac, nonprompt_frac, other_frac

def get_content_and_errors(root_hist, bins):
    rebinned_hist = root_hist.Rebin(len(bins)-1, "hnew", bins)

    bin_contents = []
    bin_errors = []
    bin_centers = []
    
    for bin in range(1, rebinned_hist.GetNbinsX() + 1):
        bin_width = rebinned_hist.GetBinWidth(bin) / 10
        bin_contents.append(rebinned_hist.GetBinContent(bin) / bin_width)
        bin_errors.append(rebinned_hist.GetBinError(bin) / bin_width)
        bin_centers.append(rebinned_hist.GetBinCenter(bin))

    bin_contents = np.array(bin_contents)
    bin_errors = np.array(bin_errors)
    bin_centers = np.array(bin_centers)

    return bin_contents, bin_errors, bin_centers

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

    # Make new ROOT histograms of the background fractions
    dy_frac, ttbar_frac, nonprompt_frac, other_frac = make_background_fraction(hist_dict)

    # Extract the bin contents and errors of each background fraction
    dy_contents, dy_errors, _ = get_content_and_errors(dy_frac, bins)
    ttbar_contents, ttbar_errors, _ = get_content_and_errors(ttbar_frac, bins)
    nonprompt_contents, nonprompt_errors, _ = get_content_and_errors(nonprompt_frac, bins)
    other_contents, other_errors, _ = get_content_and_errors(other_frac, bins)

    for i in range(len(dy_contents)):
        print(dy_contents[i]+ttbar_contents[i]+nonprompt_contents[i]+other_contents[i])

    hep.histplot(
            [other_contents, nonprompt_contents, ttbar_contents, dy_contents],
            bins=bins,
            yerr=[other_errors, nonprompt_errors, ttbar_errors, dy_errors],
            stack=False,
            histtype='errorbar',
            xerr=True,
            color=['#9c9ca1', '#964a8b', '#e42536', '#f89c20'],
            linewidth=2,
            label=[
                "Other backgrounds",
                "Nonprompt",
                r"$t\bar{t}+tW$",
                "Z+jets",
            ],
            ax=ax
    )

    hep.cms.label(data=False, fontsize=20, ax=ax)

    ratio = ttbar_frac.Clone("ttbar_dy_ratio")
    ratio.Divide(dy_frac)

    ratio_contents, ratio_errors, ratio_centers = get_content_and_errors(ratio, bins) 

    ax_ratio.errorbar(
            ratio_centers, #x
            ratio_contents, #y
            yerr=ratio_errors,#yerr
            #add xerr
            fmt='o',
            linewidth=2,
            capsize=2,
            color='black',
    )

    ax_ratio.axhline(1, color='black', linestyle='--')

    ax.set_ylabel("Background Fraction", fontsize=20)
    ax.set_ylim(0, 1.199)
    ax.yaxis.set_tick_params(labelsize=17)

    ax.set_xlim(xlim)
    ax.legend(reverse=True, fontsize=20)

    ax.set_xticklabels([])

    ax_ratio.set_ylabel(r"$\frac{t\bar{t}+tW}{Z+jets}$")
    ax_ratio.set_ylim(0, 2)
    ax_ratio.set_yticks([0, 1, 2])
    ax_ratio.yaxis.set_tick_params(labelsize=17)

    ax_ratio.set_xlim(xlim)
    ax_ratio.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}"))
    ax_ratio.set_xlabel(xlabel, fontsize=20)
    ax_ratio.xaxis.set_tick_params(labelsize=17)

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
    output_path = os.path.join("plots", channel, mll,  f"{hist_name}_efficiency.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the plot
    plt.savefig(output_path)
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
            print(f"Saved plots/{channel}/{mll}/{hist_name}_efficiency.png")

    f_in.Close()
    print(f"Finished making histograms.")
