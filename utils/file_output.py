import uproot
import os

def save_histograms(hist_dict, filename):
    directory = os.path.dirname(filename)
    histograms_directory = os.path.join(directory, 'histograms')
    os.makedirs(histograms_directory, exist_ok=True)
    with uproot.recreate(os.path.join(histograms_directory, os.path.basename(filename))) as f:
        for process in hist_dict.keys():
            for mll in hist_dict[process].keys():
                for flavor in hist_dict[process][mll].keys():
                    for histogram_name, histogram_data in hist_dict[process][mll][flavor].items():
                        hist_path = f"{process}/{mll}/{flavor}/{histogram_name}"
                        f[hist_path] = histogram_data
    
    print(f"Histograms saved to {os.path.join(histograms_directory, os.path.basename(filename))}")
