import uproot
import os
import dask
from dask.diagnostics import ProgressBar
from dask.distributed import progress
import hist
from hist import Hist

def save_histograms(my_histograms, args):
#    print("my histograms", my_histograms)

    mc_campaign = args.run
    sample = args.sample
    hnwr_mass= args.mass

    working_dir = "WR_Plotter"
    
    if mc_campaign == "Run2Summer20UL18":
        run = "Run2"
        year = "2018"
        dataset = "Summer20UL18"
    elif mc_campaign == "Run3Summer22":
        run = "Run3"
        year = "2022"
        dataset = "Summer22"
    elif mc_campaign == "Run3Summer22EE":
        run = "Run3"
        year = "2022"
        dataset = "Summer22EE"
    elif mc_campaign == "Run3Summer23":
        run = "Run3"
        year = "2023"
        dataset = "Summer23"
    elif mc_campaign == "Run3Summer23BPix":
        run = "Run3"
        year = "2023"
        dataset = "Summer23BPix"
    elif mc_campaign == "Run2Autumn18":
        dataset = "Run2Legacy"
        year = "2018"

    output_dir = working_dir+'/rootfiles/'+run+'/'+year+'/'+dataset

    Filename_prefix = "WRAnalyzer"
    Filename_suffix = ""
    Filename_skim = "_SkimTree_LRSMHighPt"

    os.makedirs(output_dir, exist_ok=True)

    if "EGamma" in sample or "SingleMuon" in sample:
        output_file = os.path.join(output_dir, f"{Filename_prefix}{Filename_skim}_data_{sample}.root")
    elif sample == "Signal":
        output_file = os.path.join(output_dir, f"{Filename_prefix}{Filename_skim}_signal_{hnwr_mass}.root")
    else:
        output_file= os.path.join(output_dir, f"{Filename_prefix}{Filename_skim}_{sample}.root")

    my_histograms = scale_hists(my_histograms)
    summed_hist = sum_hists(my_histograms)

    my_split_hists = split_hists(summed_hist)

    with uproot.recreate(output_file) as root_file:
        for key, hist in my_split_hists.items():
            region, hist_name = key
            path = f'/{region}/{hist_name}_{region}'
            root_file[path] = hist

    print(f"Histograms saved to {output_file}.")

def scale_hists(data):
    for dataset_key, dataset_info in data.items():
        if 'x_sec' in dataset_info and 'sumw' in dataset_info:
            sf = dataset_info['x_sec']/dataset_info['sumw']
            for key, value in dataset_info.items():
                if key == "cutflow":
                    # Create scaled copies of the histograms
                    cutflow_0 = value[0].copy()
                    cutflow_1 = value[1].copy()
                    
                    # Apply the scale factor
                    cutflow_0 *= sf * 59740
                    cutflow_1 *= sf * 59740
                    
                    # Update the tuple with the new scaled histograms
                    dataset_info[key] = (cutflow_0, cutflow_1, *value[2:])
                    
                    # Debugging print statements
                    print("Scaled cutflow[0]:", cutflow_0)
                    print("Scaled cutflow[1]:", cutflow_1)
                    
                elif isinstance(value, Hist):
                    # Scale the histogram directly
                    value *= sf

    return data

def sum_hists(my_hists):
    original_histograms = list(my_hists.values())[0]

    # Initialize sum_histograms for regular histograms
    sum_histograms = {
        key: Hist(*original_histograms[key].axes, storage=original_histograms[key].storage_type())
        for key in original_histograms
        if isinstance(original_histograms[key], Hist)
    }

    # Initialize sum_histograms for "cutflow" if it exists
    if "cutflow" in original_histograms:
        sum_histograms["cutflow"] = (
            original_histograms["cutflow"][0].copy(),  # First histogram in tuple
            original_histograms["cutflow"][1].copy()   # Second histogram in tuple
        )

    for dataset_info in my_hists.values():
        for key, value in dataset_info.items():
            if key == "cutflow":
                # Handle "cutflow" as a tuple
                cutflow_0, cutflow_1 = sum_histograms["cutflow"]
                cutflow_0 += value[0]  # Add the first histogram
                cutflow_1 += value[1]  # Add the second histogram

                # Update the summed "cutflow" in sum_histograms
                sum_histograms["cutflow"] = (cutflow_0, cutflow_1)

            elif isinstance(value, Hist):
                # Handle regular histograms
                hist_name = key
                hist_data = value
                if hist_name in sum_histograms:
                    sum_histograms[hist_name] += hist_data
                else:
                    sum_histograms[hist_name] = hist_data.copy()  # Initialize if not present

    return sum_histograms

def split_hists(summed_hists):
    split_histograms = {}

    for hist_name, sum_hist in summed_hists.items():
        if hist_name == "cutflow":
            # Skip the "cutflow" histogram
            continue
        process_axis = sum_hist.axes['process']
        regions_axis = sum_hist.axes['region']

        unique_processes = [process_axis.value(i) for i in range(process_axis.size)]
        unique_regions = [regions_axis.value(i) for i in range(regions_axis.size)]

        for process in unique_processes:
            for region in unique_regions:
                sub_hist = sum_hist[{process_axis.name: process, regions_axis.name: region}]
                key = (region, hist_name)
                split_histograms[key] = sub_hist

    return split_histograms
