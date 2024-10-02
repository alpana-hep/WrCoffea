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

def loop_over_mll_thresholds(channel, mll, hist_name, bkg_hist_dict, sig_hist_dict, sig_hists_event_dict, min_mll=150, max_mll=500, step=100):
    """Loop over mll thresholds, calculate efficiencies, and store results."""
    thresholds = np.arange(min_mll, max_mll + step, step)

    # ADD BACKGROUND HISTOGRAMS
    combined_hist = None
    for process, hist in bkg_hist_dict.items():
        if combined_hist is None:
            combined_hist = hist.Clone("combined_hist")
        else:
            combined_hist.Add(hist)

    sig_efficiencies = []
    sig_efficiencies_err = []
    for sig_name, sig_hist in sig_hist_dict.items():
        event_weights_hist = sig_hists_event_dict.get(sig_name)
        mll_efficiencies = []
        mll_efficiency_errors = []
        for mll_threshold in thresholds[:-1]:
            print(f"\n{sig_name}-{channel} (mll > {mll_threshold})") 
            efficiency, error = get_efficiency_for_mll_threshold(channel, mll, hist_name, combined_hist, sig_hist, event_weights_hist, mll_threshold)
            mll_efficiencies.append(efficiency)
            mll_efficiency_errors.append(error)
        sig_efficiencies.append(mll_efficiencies)
        sig_efficiencies_err.append(mll_efficiency_errors)
#        print(f"mll threshold: {mll_threshold}, Efficiency: {efficiency}, Error: {error}")
        print()
    return thresholds, sig_efficiencies, sig_efficiencies_err
#    return thresholds, efficiencies, efficiency_errors

def get_efficiency_for_mll_threshold(channel, mll, hist_name, combined_hist, sig_hist, event_weights_hist, threshold):
    """Calculate and return the efficiency histogram and plot it as a step plot."""

    # GET SIGNAL HISTOGRAM WITH MLL GREATER THAN SOME THRESHOLD
    sig_hist = filter_hist_by_mll(sig_hist, threshold)
    bkg_hist = filter_hist_by_mll(combined_hist, threshold)
    
    # GET THE LOWER AND UPPER BOUNDS ON THE SIGNAL HISTOGRAM
    lower_bound, upper_bound = compute_y_bounds(sig_hist)

    # GET THE INTEGRALS
    signal_integral, signal_error = integrate_histogram_within_bounds(sig_hist, lower_bound, upper_bound)
    background_integral, background_error = integrate_histogram_within_bounds(bkg_hist, lower_bound, upper_bound)

    print("Bkg Int.", round(background_integral, 2))
    print("S Int.", round(signal_integral, 2))

    # Integrate the event weights histogram over its entire range
    event_weights_integral = event_weights_hist.Integral(1, event_weights_hist.GetNbinsX())
    event_weights_integral = event_weights_integral * 59.74 * 1000
#    event_weights_integral = event_weights_hist.integral()  # Assuming Hist library or a similar method available

    print("Sig. SumW", round(event_weights_integral, 2))

    # Adjust signal integral by the integral of event weights
    if event_weights_integral != 0:
        signal_integral /= event_weights_integral
        signal_error /= event_weights_integral  # Adjusting error accordingly

    print(f"Sig. eff {signal_integral:.2e}")

    # CALCULATE THE EFFICIENCY
    efficiency, efficiency_error = error_on_ratio(signal_integral, signal_error, background_integral, background_error)
            
    return efficiency, efficiency_error

def filter_hist_by_mll(hist, mll_threshold):
    """
    Filter a 2D histogram to include only bins with mll values greater than the threshold,
    and preserve the bin errors.

    Args:
        hist: The original 2D histogram.
        mll_threshold: The threshold for the mll value (in GeV).

    Returns:
        A new histogram with only bins where mll > mll_threshold, including errors.
    """
    # Create a clone of the histogram to modify
    filtered_hist = hist.Clone("filtered_hist")
    filtered_hist.Reset()  # Clear the contents of the cloned histogram

    n_bins_mll = hist.GetNbinsX()
    n_bins_mlljj = hist.GetNbinsY()

    for mll_bin in range(1, n_bins_mll + 1):
        mll_center = hist.GetXaxis().GetBinCenter(mll_bin)

        # Check if mll value is greater than the threshold
        if mll_center > mll_threshold:
            for mlljj_bin in range(1, n_bins_mlljj + 1):
                content = hist.GetBinContent(mll_bin, mlljj_bin)
                error = hist.GetBinError(mll_bin, mlljj_bin)

                filtered_hist.SetBinContent(mll_bin, mlljj_bin, content*59.74*1000)
                filtered_hist.SetBinError(mll_bin, mlljj_bin, error*59.74*1000)

    return filtered_hist

def compute_y_bounds(hist):
    """Compute mean and standard deviation for the y-axis (mlljj) of a 2D histogram."""
    n_bins_mll = hist.GetNbinsX()
    n_bins_mlljj = hist.GetNbinsY()

    mlljj_values = []
    weights = []

    for mll_bin in range(1, n_bins_mll + 1):
        for mlljj_bin in range(1, n_bins_mlljj + 1):
            content = hist.GetBinContent(mll_bin, mlljj_bin)
            mlljj_center = hist.GetYaxis().GetBinCenter(mlljj_bin)
            mlljj_values.append(mlljj_center)
            weights.append(content)

    mlljj_values = np.array(mlljj_values)
    weights = np.array(weights)

    # Compute weighted mean and standard deviation
    mean = np.average(mlljj_values, weights=weights)
    variance = np.average((mlljj_values - mean)**2, weights=weights)
    stddev = np.sqrt(variance)

    lower_bound = mean - 2 * stddev
    upper_bound = mean + 2 * stddev

    print("S mean", round(mean, 2))
    print(f"(Lower, Upper) = {round(lower_bound, 2), round(upper_bound, 2)}")

    return lower_bound, upper_bound

def integrate_histogram_within_bounds(hist, lower_bound, upper_bound):
    """Integrate the histogram content and its error between lower and upper bounds on the y-axis."""
    n_bins_x = hist.GetNbinsX()
    n_bins_y = hist.GetNbinsY()

    integral = 0.0
    error_squared = 0.0

    # Loop over all bins in x and y dimensions
    for x_bin in range(1, n_bins_x + 1):
        for y_bin in range(1, n_bins_y + 1):
            y_center = hist.GetYaxis().GetBinCenter(y_bin)

            # Check if the y value is within the bounds
            if lower_bound <= y_center <= upper_bound:
                content = hist.GetBinContent(x_bin, y_bin)
                error = hist.GetBinError(x_bin, y_bin)
                integral += content
                error_squared += error ** 2

    total_error = error_squared ** 0.5
    return integral, total_error

def error_on_ratio(integral1, error1, integral2, error2):
    """Calculate the ratio and the error on the ratio integral1 / sqrt(3/2 + integral2)."""
    a = 3/2
    sqrt_b = np.sqrt(integral2)
    denominator = a + sqrt_b
    ratio = integral1 / denominator

    # Partial derivatives
    partial1 = 1 / denominator
    partial2 = -0.5 * integral1 / (sqrt_b * denominator**2)

    # Error propagation
    error_ratio = np.sqrt((partial1 * error1)**2 + (partial2 * error2)**2)

    print(f"eff/(3/2 + sqrt(B)) = {ratio} +/- {error_ratio}")
    return ratio, error_ratio

def plot_efficiency_vs_thresholds(channel, mll, hist_name, thresholds, efficiencies, efficiency_errors):
    fig, ax = plt.subplots()

    print(thresholds)
    print(efficiencies)
    # Plot efficiency using histplot
    hep.histplot(
        efficiencies,
        bins=thresholds,  # Use x_edges excluding the last edge to match y_vals length
        histtype='errorbar',
        yerr=efficiency_errors,
        xerr=True,
        color=['#5790fc', '#f89c20', '#e42536', '#964a8b', '#9c9ca1'],
        label=[r"$(m_{W_R}, m_{N})=1600,800 \mathrm{~GeV}$", r"$(m_{W_R}, m_{N})=2000,1000 \mathrm{~GeV}$", r"$(m_{W_R}, m_{N})=2400,1200 \mathrm{~GeV}$", r"$(m_{W_R}, m_{N})=2800,1400 \mathrm{~GeV}$", r"$(m_{W_R}, m_{N})=3200,1600 \mathrm{~GeV}$"],
        linewidth=2,
        ax=ax
    )

    ax.set_xlabel("$m_{ll} \mathrm{~[GeV]}$")
    ax.set_ylabel(r"$\epsilon/(3/2 + \sqrt{B})$")
    ax.set_xlim(150, 500)
    ax.set_ylim(0, 0.1)

    # Scientific notation
    ax.ticklabel_format(style="sci", scilimits=(-1, 1), axis='y', useMathText=True)
    hep.cms.label(loc=2, ax=ax)
    ax.legend()

    # Add the text box in the top-left corner based on the channel
    if channel == "mumujj":
        flavor = r"$\mu\mu$"
    elif channel == "eejj":
        flavor = r"$ee$"

    ax.text(0.05, 0.83, flavor, transform=ax.transAxes, fontsize=20,
            verticalalignment='top', horizontalalignment='left')

    # Save the plot
    plt.savefig(f'plots/mll_optimization_september/eff_over_rootB_{channel}.png')
    print(f"Saved plots/mll_optimization_september/eff_over_rootB_{channel}.png\n")

    plt.close(fig)

def fit_signal_peak(channel, mll, hist_name, sig_hist_dict, sig_hists_event_dict):
    print(hist_name, channel, mll)
    for sig_name, sig_hist in sig_hist_dict.items():
        print(sig_name, sig_hist)
        event_weights_hist = sig_hists_event_dict.get(sig_name)

if __name__ == "__main__":
    # Define input and output files
    bkg_file = "root_outputs/hists/mll_optimization_0815/all_bkgs.root"
    sig_file = "root_outputs/hists/mll_optimization_0815/all_sigs_newest.root"
    output_dir = "plots/mll_optimization"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Open the ROOT files
    bkg_root_file = ROOT.TFile(bkg_file)
    signal_root_file = ROOT.TFile(sig_file)

    # Get all histograms from the files
    bkg_histograms = get_histograms(bkg_root_file)
    signal_histograms = get_histograms(signal_root_file)

    # Organize histograms
    organized_bkg_histograms = organize_histograms(bkg_histograms)
    organized_signal_histograms = organize_histograms(signal_histograms)

    # Loop through each combination of channel, mll, and histogram
    for key, bkg_hist_dict in organized_bkg_histograms.items():
        channel, mll, hist_name = key

        if hist_name == "mass_dileptons_fourobject" and mll == "150mll" and channel == "eejj":
            grouped_bkg_histograms = group_histograms(bkg_hist_dict)
            reordered_bkg_histograms = reorder_dict(mll, grouped_bkg_histograms)

            # Loop over all signal histograms
            for signal_key, signal_hist_dict in organized_signal_histograms.items():
                sig_channel, sig_mll, sig_hist_name = signal_key
                print(sig_hist_name)
                if sig_hist_name == "mass_dileptons_fourobject" and sig_mll == mll and sig_channel == channel:
                   # Calculate efficiencies for different mll thresholds
                    event_weights_key = (sig_channel, sig_mll, "event_weight")
                    sig_hists_event_dict = organized_signal_histograms.get(event_weights_key, {})
                    thresholds, efficiencies, efficiency_errors = loop_over_mll_thresholds(channel, mll, hist_name, reordered_bkg_histograms, signal_hist_dict, sig_hists_event_dict)
                    plot_efficiency_vs_thresholds(channel, mll, hist_name, thresholds, efficiencies, efficiency_errors)

                    fit_signal_peak(channel, mll, hist_name, signal_hist_dict, sig_hists_event_dict)
    print(f"Finished making histograms.")
