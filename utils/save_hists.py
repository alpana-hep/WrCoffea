import uproot
import os
import dask
from dask.diagnostics import ProgressBar
from dask.distributed import progress
import hist
from hist import Hist

def save_histograms(toCompute, hists_name, client, executor, sample):
    output_dir = "root_outputs/hists/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{hists_name}")

#    if sample == "Signal":
#        pass
#        to_compute = remove_mass_tuples(toCompute)
#    else: 
    to_compute = toCompute

    my_histograms = compute_hists(to_compute, client, executor)

    if sample != "Signal":
        my_histograms =scale_hists(my_histograms)

    summed_hist = sum_hists(my_histograms)
    my_split_hists = split_hists(summed_hist)

    with uproot.recreate(output_file) as root_file:
        for key, hist in my_split_hists.items():
            name, process, channel, mll = key
            path = f'{process}/{channel}/{mll}/{name}'
            root_file[path] = hist

    print(f"Histograms saved to {output_file}.")

def remove_mass_tuples(data):
    new_data = {}
    for key, value in data.items():
        new_entry = value.copy()
        del new_entry['mlljj']
        del new_entry['mljj_leadlep']
        del new_entry['mljj_subleadlep']
        new_data[key] = new_entry
    return new_data

def compute_hists(all_histograms, client, executor):
        print("\nComputing histograms...")
        if executor == "umn":
            with ProgressBar():
                (histograms,)= dask.compute(all_histograms)
        elif executor=="local":
            (histograms,)= dask.compute(all_histograms)
            histograms=client.gather(histograms)
        elif executor=="lpc":
            (histograms,)= dask.compute(all_histograms)
#            histograms=client.gather(histograms)
        elif executor is None:
            with ProgressBar():
                (histograms,)= dask.compute(all_histograms)
        return histograms

def scale_hists(data):
    for dataset_key, dataset_info in data.items():
        if 'x_sec' in dataset_info and 'sumw' in dataset_info:
            sf = dataset_info['x_sec']/dataset_info['sumw']
            for key, value in dataset_info.items():
                if isinstance(value, Hist):
                    value *= sf
    return data

def sum_hists(my_hists):
    original_histograms = list(my_hists.values())[0]
    sum_histograms = {key: Hist(*original_histograms[key].axes, storage=original_histograms[key].storage_type()) for key in original_histograms if isinstance(original_histograms[key], Hist)}
    for dataset_info in my_hists.values():
        for key, value in dataset_info.items():
            if isinstance(value, Hist):
                hist_name = key
                hist_data = value
                if key in sum_histograms:
                    sum_histograms[hist_name] += hist_data
    return sum_histograms

def split_hists(summed_hists):
    split_histograms = {}

    for hist_name, sum_hist in summed_hists.items():
        process_axis = sum_hist.axes['process']
        regions_axis = sum_hist.axes['region']

        unique_processes = [process_axis.value(i) for i in range(process_axis.size)]
        unique_regions = [regions_axis.value(i) for i in range(regions_axis.size)]

        for process in unique_processes:
            for region in unique_regions:
                sub_hist = sum_hist[{process_axis.name: process, regions_axis.name: region}]
                channel, mll = region.split('_')
                key = (hist_name, process, channel, mll)
                split_histograms[key] = sub_hist

    return split_histograms
