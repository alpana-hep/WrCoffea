import uproot
import os
import dask
import numpy as np 
import awkward as ak
from distributed import Client, LocalCluster

def save_histograms(all_histograms, filename):

    #Make a flat dictionary of all of the histograms
    flat_dict = {}
    masses_dict = {}
    for key, hist_obj in all_histograms.items(): 
        if "vals" not in key:
            for hist_name, hist_data in hist_obj.__dict__.items():
                if "cuts" not in hist_name:
                    flat_dict[f"{hist_name}_{key}"] = hist_data
        elif "vals" in key:
            flat_dict[f"{key}"] = hist_obj

    #Call compute on the flat dictionary

    hist_dict = flat_dict
#    (hist_dict,) = dask.compute(flat_dict)
    
    #Create the 'histograms' directory
    directory = os.path.dirname(filename)
    histograms_directory = os.path.join(directory, 'histograms')
    os.makedirs(histograms_directory, exist_ok=True)

    #Create folders in root file and save histograms
    with uproot.recreate(os.path.join(histograms_directory, os.path.basename(filename))) as f:
        branch_types = {"mlljj": hist_dict["mlljj_vals"].type, "mljj_leadLep": hist_dict["mljj_leadLep_vals"].type, "mljj_subleadLep": hist_dict["mljj_subleadLep_vals"].type}
        tree = f.mktree("masses_tree", branch_types)

        tree.extend({"mlljj": hist_dict["mlljj_vals"], "mljj_leadLep": hist_dict["mljj_leadLep_vals"], "mljj_subleadLep": hist_dict["mljj_subleadLep_vals"]})

        for hist_name, histogram_data in hist_dict.items():
            if "vals" not in hist_name:
                for key in all_histograms.keys():
                    if key in hist_name:
                        hist_path = f"{key}/{hist_name}"
                        f[hist_path] = histogram_data

    print(f"Histograms saved to {os.path.join(histograms_directory, os.path.basename(filename))}\n")

