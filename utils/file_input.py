import json

def construct_fileset(n_files_max_per_sample):
    
    # x-secs are in pb (taken from Table 8 (p.g. 9) of AN)
    xsec_info = {
        "ttbar": 88.29,
    }

    # list of files
    with open("nanoaod_inputs.json") as f:
        file_info = json.load(f)

    # process into "fileset" summarizing all info
    fileset = {}
    for process in file_info.keys(): #ttbar
        for variation in file_info[process].keys(): #nominal
            file_list = file_info[process][variation]["files"] #list containing dictionarys with xrootd path an nevts for each nanoAOD file
            if n_files_max_per_sample != -1:
                file_list = file_list[:n_files_max_per_sample]  # use partial set of samples

            file_paths = [f["path"] for f in file_list]

            nevts_total = sum([f["nevts"] for f in file_list])
            metadata = {"process": process, "variation": variation, "nevts": nevts_total, "xsec": xsec_info[process]}
            fileset.update({f"{process}__{variation}": {"files": file_paths, "metadata": metadata}})
    return fileset
