import uproot
import os
import dask
from dask.diagnostics import ProgressBar

def save_histograms(all_histograms, hists_name):
    output_dir = "root_outputs/hists/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{hists_name}")

    with uproot.recreate(output_file) as root_file:
        hists = []
        for dataset_path, dataset_info in all_histograms.items():
            mc = dataset_info['mc']
            process = dataset_info['process']
            dataset = dataset_info['dataset']
            hist_dict = dataset_info['hist_dict']

            for region, hist_obj in hist_dict.items():
                if "vals" not in region:
                    _, channel, mll_range = region.split('_')
                    directory_path = f"{mc}/{process}/{dataset}/{channel}/{mll_range}/"
                    for hist_name, hist_data in hist_obj.__dict__.items():
                        if "cuts" not in hist_name:
                            hists.append((directory_path + hist_name, hist_data))

        print("\nComputing histograms...")
        with ProgressBar():
            (histograms,)= dask.compute(hists)

        for path, hist in histograms:
            root_file[path] = hist
            
    print(f"Histograms saved to {output_file}.")
