import ROOT
import matplotlib.pyplot as plt
import os
import numpy as np
import mplhep as hep
import array
import histogram_configs
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

def plot_histogram(channel, mll, hist_name, hist_dict):
    fig, ax = plt.subplots()
    ax.text(
        0, 1.05,               
        "Private work (CMS simulation)",              
        fontsize=24,                
        verticalalignment='top',    
        fontproperties="Tex Gyre Heros:italic",
        transform=ax.transAxes
    )
    ax.set_yscale('log')

    # Set the bins, labels and limits based on the hist_name and mll
    if hist_name in histogram_configs.configurations:
        ax.set_xlabel(histogram_configs.configurations[hist_name]["xlabel"])
        if mll in histogram_configs.configurations[hist_name]:
            config = histogram_configs.configurations[hist_name][mll]
            bins = config["bins"]
            ax.set_ylabel(config["ylabel"])
            ax.set_xlim(config["xlim"])
            ax.set_ylim(config["ylim"])

    bins = array.array('d', bins)
    bins = np.array(bins)
    # Initialize variables to hold histogram data
    hist_data = []
    labels = []

    # Define colors for each histogram stack
    colors = {
        'Z+jets': '#FFFF00',
        'tt+tW': '#FF0000',
        'Nonprompt': '#32CD32',
        'Other Backgrounds': '#00BFFF'
    }

    for process, hist in hist_dict.items():
        rebinned_hist = hist.Rebin(len(bins)-1, "hnew", bins)
        
        hist_contents = []
        for bin in range(1, rebinned_hist.GetNbinsX() + 1):
            bin_width = bins[bin] - bins[bin - 1]
            hist_contents.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)

        hist_data.append(hist_contents)
        labels.append(process)

    # Convert lists to numpy arrays for easier manipulation
    hist_data = np.array(hist_data)

    # Plot stacked histogram
    hep.histplot(
            hist_data,
            bins,
            stack=True,
            histtype='fill',
            label=labels,
            color=[colors[process] for process in labels],
            ax=ax
    )

    # Plot the uncertainties
#    ax.errorbar(
#        (bins[:-1] + bins[1:]) / 2,
#        stacked_data,
#        yerr=stacked_errors,
#        fmt='none',
#        ecolor='black',
#        capsize=2
#    )

    # Set plot labels and title
    plt.legend()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
#    hep.cms.label(data=False, lumi=59.74, fontsize=17)

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

    for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
        grouped_hist_dict = group_histograms(hist_dict)
        reordered_dict = reorder_dict(mll, grouped_hist_dict)
        plot_histogram(channel, mll, hist_name, reordered_dict)
        print(f"Saved plots/{channel}/{mll}/{hist_name}.png")

    f_in.Close()
    print(f"Finished making histograms.")
