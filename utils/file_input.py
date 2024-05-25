import json

def construct_fileset(n_files_max_per_sample):

    # x-secs are in pb (page 9 of the AN)
    xsec_info = {
        "TTTo2L2Nu": 88.29,
    }

    # Read the JSON file
    with open('nanoaod_inputs.json', 'r') as file:
        file_info = json.load(file)
    
    # process into "fileset" summarizing all info
    fileset = {}
    for mc_campaign in file_info.keys():
        for process in file_info[mc_campaign].keys():
            file_list = file_info[mc_campaign][process]["files"]
            if n_files_max_per_sample != -1:
                file_list = file_list[:n_files_max_per_sample]

            file_paths = {f["path"]: "Events" for f in file_list}

            nevts_total = sum([f["nevts"] for f in file_list])
            metadata = {"year": mc_campaign, "process": process, "nevts": nevts_total, "xsec": xsec_info[process]}
            fileset.update({f"{mc_campaign}__{process}": {"files": file_paths, "metadata": metadata}})

    return fileset
