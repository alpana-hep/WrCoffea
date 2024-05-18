import ROOT
import json
import sys

# Suppress ROOT warnings
ROOT.gErrorIgnoreLevel = ROOT.kError

def get_nevents_from_root_file(filepath):
    try:
        file = ROOT.TFile.Open(filepath)
        if not file or file.IsZombie():
            print(f"Error: Could not open file {filepath}", file=sys.stderr)
            return 0
        
        tree = file.Get("Events")
        if not tree:
            print(f"Error: Could not find 'Events' tree in file {filepath}", file=sys.stderr)
            return 0
        
        nevts = tree.GetEntries()
        file.Close()
        return nevts
    except Exception as e:
        print(f"Exception occurred while processing file {filepath}: {e}", file=sys.stderr)
        return 0

def parse_txt_file(input_file):
    data = {}
    with open(input_file, 'r') as f:
        lines = f.readlines()
        total_nevts = 0
        files_data = []
        for line in lines:
            filepath = line.strip()
            filepath_with_prefix = "root://cmsxrootd.fnal.gov/" + filepath
            nevts = get_nevents_from_root_file(filepath_with_prefix)
            total_nevts += nevts
            files_data.append({'path': filepath_with_prefix, 'nevts': nevts})
        
        data['ttbar'] = {
            'nominal': {
                'nevts_total': total_nevts,
                'files': files_data
            }
        }
    return data

def write_json_file(data, output_file):
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    input_file = "datasets/ttbar/ttbar_2018.txt"
    output_file = "nanoaod_inputs.json"
    data = parse_txt_file(input_file)
    write_json_file(data, output_file)

