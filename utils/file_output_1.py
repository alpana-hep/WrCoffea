import uproot
import os
import dask
import numpy as np 
import awkward as ak
from distributed import Client, LocalCluster

def save_histograms(all_histograms, filename):
# Create a ROOT file
    with uproot.recreate(f"{filename}") as root_file:
        for sample, sample_info in all_histograms.items():
            mc = sample_info['mc']
            process = sample_info['process']
            hist_dict = sample_info['hist_dict']

            for region, hist_obj in hist_dict.items():
                if "vals" not in region:
                    print("Region: ", region)
                    channel, mll_range = region.split('_')
                    directory_path = f"{mc}/{process}/{channel}/{mll_range}/"
                    print("directory_path:", directory_path)
                    for hist_name, hist_data in hist_obj.__dict__.items():
                        if "cuts" not in hist_name:
#                            print(f"Hist name: {hist_name}")
                            print(f"hist_data: {type(hist_data)}")
                            root_file[directory_path + hist_name] = hist_data

    print("ROOT file created successfully.")
