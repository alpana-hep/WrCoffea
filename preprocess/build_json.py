import ROOT
import json
import sys
import subprocess

# Suppress ROOT warnings
ROOT.gErrorIgnoreLevel = ROOT.kError

def get_genevents_from_root_file(filepath):
    try:
        file = ROOT.TFile.Open(filepath)
        if not file or file.IsZombie():
            print(f"Error: Could not open file {filepath}", file=sys.stderr)
            return 0, 0.0, 0.0

        runs_tree = file.Get("Runs")
        if not runs_tree:
            print(f"Error: Could not find 'Runs' tree in file {filepath}", file=sys.stderr)
            return 0, 0.0, 0.0

        genEventCount = 0
        genEventSumw = 0.0
        genEventSumw2 = 0.0
        
        for entry in runs_tree:
            genEventCount += getattr(entry, 'genEventCount', 0)
            genEventSumw += getattr(entry, 'genEventSumw', 0.0)
            genEventSumw2 += getattr(entry, 'genEventSumw2', 0.0)

        file.Close()
        return genEventCount, genEventSumw, genEventSumw2
    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0, 0.0, 0.0

def query_das(das_name):
    command = f'dasgoclient -query="file dataset={das_name}"'
    result = subprocess.run(command, shell=True, text=True, capture_output=True)
    files = result.stdout.strip().split('\n')
    return files

def parse_txt_file(config):
    data = {}

    for dataset_name, metadata in config.items():
        print("Preprocessing", dataset_name)
        files = query_das(dataset_name)
        files_with_prefix = [f'root://cmsxrootd.fnal.gov/{file}' for file in files if file]
        dataset_data = {
            "files": {file: "Events" for file in files_with_prefix},
            "metadata": {
                "mc_campaign": "UL2018",
                "process": metadata["process"],
                "dataset": metadata["dataset"],
                "xsec": metadata["xsec"],
                "genEventCount": 0,
                "genEventSumw": 0.0,
                "genEventSumw2": 0.0
            }
        }

        for file in files_with_prefix:
            genEventCount, genEventSumw, genEventSumw2 = get_genevents_from_root_file(file)
            dataset_data["metadata"]["genEventCount"] += genEventCount
            dataset_data["metadata"]["genEventSumw"] += genEventSumw
            dataset_data["metadata"]["genEventSumw2"] += genEventSumw2
        data[dataset_name] = dataset_data

    return data

def write_json_file(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

def load_config(filepath):
    with open(filepath, 'r') as file:
        return json.load(file)

if __name__ == "__main__":
    output_file = "nanoaod_inputs.json"
    config = load_config("xsec_process_config.json")
    data = parse_txt_file(config)

    write_json_file(data, output_file)
