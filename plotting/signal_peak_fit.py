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

def loop_over_mll_thresholds(channel, mll, hist_name, bkg_hist_dict, sig_hist_dict, sig_hists_event_dict, min_mll=150, max_mll=550, step=50):
    """Loop over mll thresholds, calculate efficiencies, and store results."""
    thresholds = np.arange(min_mll, max_mll + step, step)

    sig_mean = []
    sig_stddev = []
    fit_mean = []
    fit_stddev = []

    for sig_name, sig_hist in sig_hist_dict.items():
        event_weights_hist = sig_hists_event_dict.get(sig_name)
        mll_sig_mean = []
        mll_sig_stddev = []
        mll_fit_mean = []
        mll_fit_stddev = []
        for mll_threshold in thresholds[:-1]:
            print(f"\n{sig_name}-{channel} (mll > {mll_threshold})") 
            signal_mean, signal_stddev, fitted_mean, fitted_stddev, bin_edges, y_vals  = fit_gaussian_for_mll_threshold(channel, mll, hist_name, sig_hist, event_weights_hist, mll_threshold)
            if sig_name == "MWR2000_MN1000" and channel == "eejj" and mll_threshold==150:
                plot_signal_hist(channel, mll_threshold, sig_name, bin_edges, y_vals, signal_mean, signal_stddev)
            mll_sig_mean.append(signal_mean)
            mll_sig_stddev.append(signal_stddev)
            mll_fit_mean.append(fitted_mean)
            mll_fit_stddev.append(fitted_stddev)
        sig_mean.append(mll_sig_mean)
        sig_stddev.append(mll_sig_stddev)
        fit_mean.append(mll_fit_mean)
        fit_stddev.append(mll_fit_stddev)
#        print(f"mll threshold: {mll_threshold}, Efficiency: {efficiency}, Error: {error}")
    return sig_mean, sig_stddev, fit_mean, fit_stddev

#    return thresholds, efficiencies, efficiency_errors

def fit_gaussian_for_mll_threshold(channel, mll, hist_name, sig_hist, event_weights_hist, threshold):

    sig_hist = filter_hist_by_mll(sig_hist, threshold)
    
    mean, sd, bin_centers, y_vals = compute_stats(sig_hist)
    print(f"Non-fitted parameters: Mean = {mean}, Stddev = {sd}") 
    popt, pcov = curve_fit(gaussian, bin_centers, y_vals, p0=[max(y_vals), bin_centers[np.argmax(y_vals)], 10])

    amplitude, mu, stddev = popt
    print(f"Fitted parameters: Amplitude = {amplitude}, Mean = {mu}, Stddev = {stddev}")
            
    return mean, sd,  mu, stddev, bin_centers,y_vals

def filter_hist_by_mll(hist, mll_threshold):
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

                filtered_hist.SetBinContent(mll_bin, mlljj_bin, content)
                filtered_hist.SetBinError(mll_bin, mlljj_bin, error)

    return filtered_hist

def compute_stats(hist):
    """Compute mean and standard deviation for the y-axis (mlljj) of a 2D histogram."""
    n_bins_mll = hist.GetNbinsX()
    n_bins_mlljj = hist.GetNbinsY()

    mlljj_weights = []
    bins = []
    proj_y = hist.ProjectionY()

    for mlljj_bin in range(1, n_bins_mlljj + 1):
        y_bin_content = 0
        for mll_bin in range(1, n_bins_mll + 1):
            content = hist.GetBinContent(mll_bin, mlljj_bin)
            y_bin_content += hist.GetBinContent(mll_bin, mlljj_bin)
        mlljj_weights.append(y_bin_content)
          
        mlljj_center = hist.GetYaxis().GetBinCenter(mlljj_bin)
        bins.append(mlljj_center)
         
    mlljj_values = np.array(bins)
    weights = np.array(mlljj_weights)

    # Compute weighted mean and standard deviation
    mean = np.average(mlljj_values, weights=weights)
    variance = np.average((mlljj_values - mean)**2, weights=weights)
    stddev = np.sqrt(variance)

    return mean, stddev, mlljj_values, weights

def plot_signal_hist(channel, mll, hist_name, bins, mlljj_values, sig_mean, signal_stddev):
    fig, ax = plt.subplots()

    bins = np.arange(0, 8010, 10)
    hep.histplot(
        mlljj_values,
        bins=bins,  
        histtype='step',
        color=['#5790fc'],
        label=[r"$(m_{W_R}, m_{N})=2000,1000 \mathrm{~GeV}$"],
        linewidth=2,
        ax=ax
    )

    #GUASSIAN FIT
    bin_centers = 0.5 * (bins[:-1] + bins[1:])  # Compute bin centers
    initial_guess = [max(mlljj_values), np.mean(bin_centers), np.std(bin_centers)]  # Initial guess for fit parameters
    popt, pcov = curve_fit(gaussian, bin_centers, mlljj_values, p0=initial_guess)
    amplitude, mean, stddev = popt

    # PLOT GUASSIAN FIT
    x_fit = np.linspace(0, 4000, 1000)  # Generate x values for the fitted curve
    y_fit = gaussian(x_fit, *popt)
    ax.plot(x_fit, y_fit, color='red', linestyle='-', lw=2)

    # PLOT GAUSSIAN MEAN
    y_min, y_max = ax.get_ylim()
    ax.set_ylim(0, y_max * 1.5)
    gaussian_at_mean = gaussian(mean, *popt)
    ymax_scaled = gaussian_at_mean / ax.get_ylim()[1]  # Scale the height of the line to fit within the y-axis limits
    ax.axvline(mean, color='red', linestyle='--', ymax=ymax_scaled, lw=2, label=f'Fit $\mu$ = {mean:.2f} GeV')

    # PLOT GAUSSIAN STDDEV
    x_stddev_fill = np.linspace(mean - stddev, mean + stddev, 100)
    y_stddev_fill = gaussian(x_stddev_fill, *popt)
    ax.fill_between(x_stddev_fill, y_stddev_fill, color='red', alpha=0.3, label=f'Fit $\sigma$  = {abs(stddev):.2f} GeV')

    # PLOT SIGNAL MEAN
    ax.axvline(x=sig_mean, ymin=0, ymax=0.4, color='#5790fc', linestyle='--', lw=2, label=f'Sig. $\mu$ = {sig_mean:.2f} GeV')

    # PLOT SIGNAL STDDEV
    x_sig_stddev_fill = np.linspace(sig_mean - signal_stddev, sig_mean + signal_stddev, 100)
    y_sig_stddev_fill = np.interp(x_sig_stddev_fill, bin_centers, mlljj_values)
    ax.fill_between(x_sig_stddev_fill, 0, y_sig_stddev_fill, color='#5790fc', alpha=0.3, label=f'Sig. $\sigma$ = {abs(signal_stddev):.2f} GeV')

    ax.set_xlabel("$m_{lljj} \mathrm{~[GeV]}$")
    ax.set_ylabel(r"Events / 10 GeV")
    ax.ticklabel_format(style="sci", scilimits=(-1, 1), axis='y', useMathText=True)
    ax.set_xlim(0, 4000)

    # Scientific notation
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
    plt.savefig(f'plots/mll_optimization_september/{hist_name}_signal_peak_{channel}.png', dpi=600)
    print(f"Saved plots/mll_optimization_september/{hist_name}_signal_peak_{channel}.png\n")

    plt.close(fig)

def gaussian(x, amplitude, mean, stddev):
    return amplitude * np.exp(-((x - mean) ** 2) / (2 * stddev ** 2))

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
                if sig_hist_name == "mass_dileptons_fourobject" and sig_mll == mll and sig_channel == channel:
                   # Calculate efficiencies for different mll thresholds
                    event_weights_key = (sig_channel, sig_mll, "event_weight")
                    sig_hists_event_dict = organized_signal_histograms.get(event_weights_key, {})
                    sig_mean, sig_stddev, fit_mean, fit_stddev,  = loop_over_mll_thresholds(channel, mll, hist_name, reordered_bkg_histograms, signal_hist_dict, sig_hists_event_dict)
#                    plot_efficiency_vs_thresholds(channel, mll, hist_name, thresholds, efficiencies, efficiency_errors)

    print(f"Finished making histograms.")
