import uproot
import os
import dask

def save_histograms(all_histograms, filename):

    print("Computing and saving histograms...")

    #Make a flat dictionary of all of the histograms
    flat_dict = {}
    for key, hist_obj in all_histograms.items(): 
        for hist_name, hist_data in hist_obj.__dict__.items():
            if "cuts" not in hist_name:
                flat_dict[f"{hist_name}_{key}"] = hist_data

    #Call compute on the flat dictionary
    (hist_dict,) = dask.compute(flat_dict)

    #Create the 'histograms' directory
    directory = os.path.dirname(filename)
    histograms_directory = os.path.join(directory, 'histograms')
    os.makedirs(histograms_directory, exist_ok=True)

    #Create folders in root file and save histograms
    with uproot.recreate(os.path.join(histograms_directory, os.path.basename(filename))) as f:
        for hist_name, histogram_data in hist_dict.items():
            for key in all_histograms.keys():
                if key in hist_name:
                    hist_path = f"{key}/{hist_name}"
                    f[hist_path] = histogram_data

    print(f"Histograms saved to {os.path.join(histograms_directory, os.path.basename(filename))}")

