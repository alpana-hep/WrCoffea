import os
import ROOT
import re
import json
import subprocess

def extract_genmodel_fields_from_lines(lines):
    pattern = re.compile(r"GenModel_WRtoNLtoLLJJ_MWR(\d+)_MN(\d+)_TuneCP5_13TeV_madgraph_pythia8")
    mwr_mn_files = {}

    for file_name in lines:
        root_file = ROOT.TFile.Open(file_name)
        if not root_file or root_file.IsZombie():
            print(f"Failed to open file {file_name}")
            continue

        tree = root_file.Get("Events")
        if not tree:
            print(f"Failed to get 'Events' tree in file {file_name}")
            root_file.Close()
            continue

        branches = tree.GetListOfBranches()
        for branch in branches:
            branch_name = branch.GetName()
            match = pattern.match(branch_name)
            if match:
                mwr = match.group(1)
                mn = match.group(2)
                key = f"MWR{mwr}_MN{mn}"

                if key not in mwr_mn_files:
                    mwr_mn_files[key] = {
                        "files": {},
                        "metadata": {
                            "mc_campaign": "PL18",
                            "lumi": 59.74,
                            "process": "Signal",
                            "dataset": key,
                            "xsec": 1
                        }
                    }
                mwr_mn_files[key]["files"][file_name] = "Events"

        root_file.Close()

    return mwr_mn_files

# Step 1: Retrieve dataset files using DAS client and store results in memory
datasets = {
    'WRtoNLtoLLJJ': [
        "/WRtoNLtoLLJJ_MWR500to3500_TuneCP5-madgraph-pythia8/RunIIAutumn18NanoAODv7-Nano02Apr2020_rpscan_102X_upgrade2018_realistic_v21-v1/NANOAODSIM",
    ],
}

file_contents = ""

for s, dList in datasets.items():
    for d in dList:
        print(f'Finding {s} samples for {d}')
        result = subprocess.run(['dasgoclient', '-query', f'file dataset={d}'], capture_output=True, text=True)
        file_contents += result.stdout

# Step 2: Prepend string to each line in the retrieved file contents
prepend_string = 'root://eoscms.cern.ch:1094//eos/cms'
lines = file_contents.strip().split('\n')
prepended_lines = [f'{prepend_string}{line}' for line in lines]

# Step 3: Extract MWR and MN values from the ROOT files and save to JSON
output_json_path = "signal2018.json"
print("\nCreating json file...\n")

mwr_mn_files = extract_genmodel_fields_from_lines(prepended_lines)

with open(output_json_path, 'w') as json_file:
    json.dump(mwr_mn_files, json_file, indent=2)

print(f"Signal json file saved to {output_json_path}")
