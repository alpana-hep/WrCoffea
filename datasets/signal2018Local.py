import os
import re
import json
import uproot

def extract_genmodel_fields_from_lines(lines):
    pattern = re.compile(r"GenModel_WRtoNLtoLLJJ_MWR(\d+)_MN(\d+)_TuneCP5_13TeV_madgraph_pythia8")
    mwr_mn_files = {}

    for file_name in lines:
        try:
            root_file = uproot.open(file_name)
        except Exception as e:
            print(f"Failed to open file {file_name}: {e}")
            continue

        if "Events" not in root_file:
            print(f"Failed to get 'Events' tree in file {file_name}")
            continue

        tree = root_file["Events"]
        branch_names = tree.keys()

        for branch_name in branch_names:
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

    return mwr_mn_files

# List files in the directory
prepended_lines = [os.path.join('datasets/2018_signal_prelegacy/', f) for f in os.listdir('datasets/2018_signal_prelegacy/') if os.path.isfile(os.path.join('datasets/2018_signal_prelegacy/', f))]

# Specify output JSON path
output_json_path = "signal2018Local.json"
print("\nCreating json file...\n")

# Extract genmodel fields from files
mwr_mn_files = extract_genmodel_fields_from_lines(prepended_lines)

# Write to JSON file
with open(output_json_path, 'w') as json_file:
    json.dump(mwr_mn_files, json_file, indent=2)

print(f"Signal json file saved to {output_json_path}")

