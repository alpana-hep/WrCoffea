import os
import json
import argparse

# Function to query DAS and get the list of files
def query_das(das_name):
    command = f'dasgoclient -query="file dataset={das_name}"'
    result = os.popen(command).read()
    files = result.strip().split('\n')
    return files

def construct_fileset(dataset):
    UL_bkg = getattr(__import__(dataset), dataset)

    # Build the fileset dictionary
    fileset = {}
    for dataset_name, info in UL_bkg.items():
        das_name = info['das_name']
        files = query_das(das_name)

        # Prepend root://cmsxrootd.fnal.gov/ to each file path
        files = [f'root://cmsxrootd.fnal.gov/{file}' for file in files]

        # Create a dictionary of files with "Events" as the value for each file
        files_dict = {file: "Events" for file in files}

        # Add metadata
        metadata = {
            "lumi": info["lumi"],
            "xsec": info["xsec"],
            "process": info["process"],
            "mc_campaign": info["mc_campaign"],
        }

        # Add to fileset
        fileset[dataset_name] = {
            "files": files_dict,
            "metadata": metadata,
        }

    # Specify the directory to save JSON files
    output_directory = 'filesets'

    # Create the directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Save the output dictionary to a file in the filesets directory
    output_file = os.path.join(output_directory, f'{dataset}.json')
    with open(output_file, 'w') as f:
        json.dump(fileset, f, indent=4)

    print(f"Constructed fileset saved to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Construct fileset from dataset.')
    parser.add_argument('dataset', choices=['UL18_bkg', 'UL17_bkg', 'UL16_bkg'], help='Choose the dataset to construct fileset from')
    args = parser.parse_args()
    
    construct_fileset(args.dataset)
