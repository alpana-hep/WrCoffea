import json

def construct_fileset():
    with open("nanoaod_inputs.json") as f:
        file_info = json.load(f)
    fileset = {}
    for process in file_info.keys():
        for variation in file_info[process].keys():
            file_list = file_info[process][variation]["files"]
            file_paths = [f["path"] for f in file_list]
            fileset.update({f"{process}__{variation}": {"files": file_paths}})
    return fileset
