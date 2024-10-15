import ROOT
import matplotlib.pyplot as plt
import os
import numpy as np
import mplhep as hep
import array
import histogram_configs
import matplotlib.ticker as mticker
from scipy.optimize import curve_fit

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

def exp_decreasing(x, a, b):
    return a * np.exp(-b * x)

def plot_histogram(channel, mll, hist_name, hist_dict, data_hist=None, signal_hist=None):
    fig, ax = plt.subplots()

    if hist_name in histogram_configs.configurations:
        xlabel = histogram_configs.configurations[hist_name]["xlabel"]
        if mll in histogram_configs.configurations[hist_name]:
            config = histogram_configs.configurations[hist_name][mll]
            bins = np.array(array.array('d', config["bins"]))
            ylabel = config["ylabel"]
            xlim = config["xlim"]
            ylim = config["ylim"]

    dy, dy_err, bin_centers, bin_widths = [], [], [], []

    for process, hist in hist_dict.items():
        if process == 'Z+jets':
            rebinned_hist = hist.Rebin(len(bins)-1, "hnew", bins)
            for bin in range(1, rebinned_hist.GetNbinsX() + 1):
                bin_center = rebinned_hist.GetBinCenter(bin)
                bin_width =  rebinned_hist.GetBinWidth(bin)
                bin_content = rebinned_hist.GetBinContent(bin) * 59.74 * 1000
                bin_error = rebinned_hist.GetBinError(bin) * 59.74 * 1000
                bin_centers.append(bin_center)
                dy.append(bin_content)
                dy_err.append(bin_error)
                bin_widths.append(bin_width)

    bin_centers = np.array(bin_centers)
    bin_widths = np.array(bin_widths)
    dy = np.array(dy)
    dy_err = np.array(dy_err)

    # Plot original data and fitted curve
    hep.histplot(dy, bins=bins, yerr = dy_err, histtype='step', label='Z+jets', color='blue', ax=ax)

    # Filter the data for bin centers between 1000 and 5000
    mask = (bin_centers >= 1000) & (bin_centers <= 4000)
    filtered_bin_centers = bin_centers[mask]
    filtered_dy = dy[mask]
    filtered_dy_err = dy_err[mask]

    # Initial guesses for the parameters a and b based on the data range
    a_initial = np.max(filtered_dy)  # Initial guess for a: max value of filtered_dy
    b_initial = 0.001  # A reasonable small value for b

    try:
        popt, pcov = curve_fit(
            exp_decreasing,
            filtered_bin_centers,
            filtered_dy,
            sigma=filtered_dy_err,
            absolute_sigma=True,
            p0=[a_initial, b_initial],
        )

        fit_values = exp_decreasing(filtered_bin_centers, *popt)
        ax.plot(filtered_bin_centers, fit_values, label=f'Exp. Fit', color='red', lw=1)

        a_fitted, b_fitted = popt
        a_err, b_err = np.sqrt(np.diag(pcov))

        # Calculate the uncertainty (band) around the fit using error propagation
        delta_fit = np.sqrt(
            (exp_decreasing(filtered_bin_centers, a_fitted + a_err, b_fitted) - fit_values) ** 2 +
            (exp_decreasing(filtered_bin_centers, a_fitted, b_fitted + b_err) - fit_values) ** 2
        )

        # Plot the uncertainty band around the fitted curve
        ax.fill_between(filtered_bin_centers, fit_values - delta_fit, fit_values + delta_fit, color='green', alpha=0.5, label="Fit Uncert.")

    except RuntimeError as e:
        print(f"Fit failed: {e}")

    # Labels and formatting
    ax.set_xlabel(xlabel)

    # Add the text box in the top-left corner
    if channel == "eejj":
        flavor = r"$ee$"
        if mll == "150mll":
            region = "$m_{ll} > 150 \mathrm{~GeV}$"
    ax.text(0.05, 0.96, flavor, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')
    ax.text(0.05, 0.91, region, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')

    ax.set_ylabel(ylabel)
    ax.set_xlim(xlim)
    ax.set_ylim(1e-2, 1e4)
    ax.set_yscale('log')
    ax.legend()


    # Save plot
    output_path = os.path.join("plots", channel, mll, f"{hist_name}_with_fit.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=600)
    plt.close()

    print(f"Saved {output_path}")

if __name__ == "__main__":
    input_file = "root_outputs/hists/mll_optimization_0815/all_bkgs.root"
    f_in = ROOT.TFile(input_file, "READ")
    my_histos = get_histograms(f_in)
    sorted_histograms = organize_histograms(my_histos)

    for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
        grouped_hist_dict = group_histograms(hist_dict)
        reordered_dict = reorder_dict(mll, grouped_hist_dict)
        if hist_name == "mass_fourobject" and mll == "150mll" and channel == "eejj":
            plot_histogram(channel, mll, hist_name, reordered_dict)
        else:
            continue

    f_in.Close()
    print(f"Finished making histograms.")
