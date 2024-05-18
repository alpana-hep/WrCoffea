import json

def construct_fileset(n_files_max_per_sample):
    # Read the JSON file
    with open('nanoaod_inputs.json', 'r') as file:
        data = json.load(file)
    
    # Initialize the resulting dictionary
    file_info = {
        'ttbar': {
            "files": {}
        }
    }
    
    # Process the data to fill the file_info dictionary
    if n_files_max_per_sample != -1:
        files_to_process = data['ttbar']['nominal']['files'][:n_files_max_per_sample]
    else:
        files_to_process = data['ttbar']['nominal']['files']

    for file_entry in files_to_process:
        path = file_entry['path']
        file_info['ttbar']['files'][path] = "Events"
    
    return file_info
