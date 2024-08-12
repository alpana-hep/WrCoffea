import os
import json

def generate_json(directory_structure):
    data = {}
    
    for dataset, runs in directory_structure.items():
        for run, files in runs.items():
            path = f"/{dataset}/Run2018{run}-UL2018_MiniAODv2_NanoAODv9-v2/NANOAOD"
            data[path] = {
                "files": {},
                "metadata": {
                    "mc_campaign": "UL2018",
                    "process": dataset,
                    "dataset": f"Run2018{run}"
                }
            }
            for file in files:
                full_path = os.path.abspath(file)
                data[path]["files"][full_path] = "Events"
    
    return data

def main():
    base_dir = "dataskims/"  # Change this to your base directory
    directories = {
        "SingleMuon": {
            "A": ["SingleMuon2018RunA_part1-30.root", "SingleMuon2018RunA_part31-60.root", "SingleMuon2018RunA_part61-92.root"],
            "B": ["SingleMuon2018RunB_part1-25.root", "SingleMuon2018RunB_part26-51.root"],
            "C": ["SingleMuon2018RunC_part1-28.root", "SingleMuon2018RunC_part29-56.root"],
            "D": ["SingleMuon2018RunD_part1-30.root", "SingleMuon2018RunD_part31-60.root", "SingleMuon2018RunD_part61-90.root", "SingleMuon2018RunD_part91-120.root", "SingleMuon2018RunD_part121-150.root", "SingleMuon2018RunD_part151-194.root"]
        },
    }

    # Convert relative paths to absolute paths
    directory_structure = {}
    for dataset, runs in directories.items():
        directory_structure[dataset] = {}
        for run, files in runs.items():
            directory_structure[dataset][run] = [os.path.join(base_dir, f"{dataset}_2018_Run{run}_lepPt45", file) for file in files]

    json_data = generate_json(directory_structure)
    
    output_file = os.path.join(base_dir, "UL2018_skimmed_data.json")
    with open(output_file, 'w') as f:
        json.dump(json_data, f, indent=2)
    
    print(f"JSON file has been written to {output_file}")

if __name__ == "__main__":
    main()

