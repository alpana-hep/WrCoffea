import json

def construct_fileset(n_files_max_per_sample):

    # x-secs are in pb (page 9 of the AN)
    xsec_info = {
        "ttbar": 88.29,
    }

    # Read the JSON file
    with open('nanoaod_inputs.json', 'r') as file:
        file_info = json.load(file)
    
    # process into "fileset" summarizing all info
    fileset = {}
    for process in file_info.keys():
        for variation in file_info[process].keys():
            file_list = file_info[process][variation]["files"]
            if n_files_max_per_sample != -1:
                file_list = file_list[:n_files_max_per_sample]

            file_paths = {f["path"]: "Events" for f in file_list}

            nevts_total = sum([f["nevts"] for f in file_list])
            metadata = {"process": process, "variation": variation, "nevts": nevts_total, "xsec": xsec_info[process]}
            fileset.update({f"{process}__{variation}": {"files": file_paths, "metadata": metadata}})

    return fileset
