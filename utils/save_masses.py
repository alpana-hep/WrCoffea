import uproot
import os
import dask
from dask.diagnostics import ProgressBar
import numpy as np

def save_histogram_data(directory_path, data):
    os.makedirs(directory_path, exist_ok=True)
    with open(os.path.join(directory_path, "data.txt"), "w") as f:
        f.write(str(data))

def save_data_to_directories(all_tuples):
    base_path = "mass_tuples"  # Base path where directories will be created
    mass_tuples = []

    for dataset, data in all_tuples.items():
        if 'mlljj_eejj_60mll150' in data:
            directory_path = os.path.join(base_path, "eejj/60mll150/mlljj")
            save_histogram_data(directory_path, data['mlljj_eejj_60mll150'])
            mass_tuples.append((directory_path, data['mlljj_eejj_60mll150']))

        if 'mljj_leadlep_eejj_60mll150' in data:
            directory_path = os.path.join(base_path, "eejj/60mll150/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_eejj_60mll150'])
            mass_tuples.append((directory_path, data['mljj_leadlep_eejj_60mll150']))

        if 'mljj_subleadlep_eejj_60mll150' in data:
            directory_path = os.path.join(base_path, "eejj/60mll150/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_eejj_60mll150'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_eejj_60mll150']))

        if 'mlljj_mumujj_60mll150' in data:
            directory_path = os.path.join(base_path, "mumujj/60mll150/mlljj")
            save_histogram_data(directory_path, data['mlljj_mumujj_60mll150'])
            mass_tuples.append((directory_path, data['mlljj_mumujj_60mll150']))

        if 'mljj_leadlep_mumujj_60mll150' in data:
            directory_path = os.path.join(base_path, "mumujj/60mll150/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_mumujj_60mll150'])
            mass_tuples.append((directory_path, data['mljj_leadlep_mumujj_60mll150']))

        if 'mljj_subleadlep_mumujj_60mll150' in data:
            directory_path = os.path.join(base_path, "mumujj/60mll150/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_mumujj_60mll150'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_mumujj_60mll150']))

        if 'mlljj_emujj_60mll150' in data:
            directory_path = os.path.join(base_path, "emujj/60mll150/mlljj")
            save_histogram_data(directory_path, data['mlljj_emujj_60mll150'])
            mass_tuples.append((directory_path, data['mlljj_emujj_60mll150']))

        if 'mljj_leadlep_emujj_60mll150' in data:
            directory_path = os.path.join(base_path, "emujj/60mll150/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_emujj_60mll150'])
            mass_tuples.append((directory_path, data['mljj_leadlep_emujj_60mll150']))

        if 'mljj_subleadlep_emujj_60mll150' in data:
            directory_path = os.path.join(base_path, "emujj/60mll150/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_emujj_60mll150'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_emujj_60mll150']))

        if 'mlljj_eejj_150mll400' in data:
            directory_path = os.path.join(base_path, "eejj/150mll400/mlljj")
            save_histogram_data(directory_path, data['mlljj_eejj_150mll400'])
            mass_tuples.append((directory_path, data['mlljj_eejj_150mll400']))

        if 'mljj_leadlep_eejj_150mll400' in data:
            directory_path = os.path.join(base_path, "eejj/150mll400/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_eejj_150mll400'])
            mass_tuples.append((directory_path, data['mljj_leadlep_eejj_150mll400']))

        if 'mljj_subleadlep_eejj_150mll400' in data:
            directory_path = os.path.join(base_path, "eejj/150mll400/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_eejj_150mll400'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_eejj_150mll400']))

        if 'mlljj_mumujj_150mll400' in data:
            directory_path = os.path.join(base_path, "mumujj/150mll400/mlljj")
            save_histogram_data(directory_path, data['mlljj_mumujj_150mll400'])
            mass_tuples.append((directory_path, data['mlljj_mumujj_150mll400']))

        if 'mljj_leadlep_mumujj_150mll400' in data:
            directory_path = os.path.join(base_path, "mumujj/150mll400/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_mumujj_150mll400'])
            mass_tuples.append((directory_path, data['mljj_leadlep_mumujj_150mll400']))

        if 'mljj_subleadlep_mumujj_150mll400' in data:
            directory_path = os.path.join(base_path, "mumujj/150mll400/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_mumujj_150mll400'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_mumujj_150mll400']))

        if 'mlljj_emujj_150mll400' in data:
            directory_path = os.path.join(base_path, "emujj/150mll400/mlljj")
            save_histogram_data(directory_path, data['mlljj_emujj_150mll400'])
            mass_tuples.append((directory_path, data['mlljj_emujj_150mll400']))

        if 'mljj_leadlep_emujj_150mll400' in data:
            directory_path = os.path.join(base_path, "emujj/150mll400/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_emujj_150mll400'])
            mass_tuples.append((directory_path, data['mljj_leadlep_emujj_150mll400']))

        if 'mljj_subleadlep_emujj_150mll400' in data:
            directory_path = os.path.join(base_path, "emujj/150mll400/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_emujj_150mll400'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_emujj_150mll400']))

        if 'mlljj_eejj_400mll' in data:
            directory_path = os.path.join(base_path, "eejj/400mll/mlljj")
            save_histogram_data(directory_path, data['mlljj_eejj_400mll'])
            mass_tuples.append((directory_path, data['mlljj_eejj_400mll']))

        if 'mljj_leadlep_eejj_400mll' in data:
            directory_path = os.path.join(base_path, "eejj/400mll/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_eejj_400mll'])
            mass_tuples.append((directory_path, data['mljj_leadlep_eejj_400mll']))

        if 'mljj_subleadlep_eejj_400mll' in data:
            directory_path = os.path.join(base_path, "eejj/400mll/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_eejj_400mll'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_eejj_400mll']))

        if 'mlljj_mumujj_400mll' in data:
            directory_path = os.path.join(base_path, "mumujj/400mll/mlljj")
            save_histogram_data(directory_path, data['mlljj_mumujj_400mll'])
            mass_tuples.append((directory_path, data['mlljj_mumujj_400mll']))

        if 'mljj_leadlep_mumujj_400mll' in data:
            directory_path = os.path.join(base_path, "mumujj/400mll/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_mumujj_400mll'])
            mass_tuples.append((directory_path, data['mljj_leadlep_mumujj_400mll']))

        if 'mljj_subleadlep_mumujj_400mll' in data:
            directory_path = os.path.join(base_path, "mumujj/400mll/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_mumujj_400mll'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_mumujj_400mll']))

        if 'mlljj_emujj_400mll' in data:
            directory_path = os.path.join(base_path, "emujj/400mll/mlljj")
            save_histogram_data(directory_path, data['mlljj_emujj_400mll'])
            mass_tuples.append((directory_path, data['mlljj_emujj_400mll']))

        if 'mljj_leadlep_emujj_400mll' in data:
            directory_path = os.path.join(base_path, "emujj/400mll/mljj_leadlep")
            save_histogram_data(directory_path, data['mljj_leadlep_emujj_400mll'])
            mass_tuples.append((directory_path, data['mljj_leadlep_emujj_400mll']))

        if 'mljj_subleadlep_emujj_400mll' in data:
            directory_path = os.path.join(base_path, "emujj/400mll/mljj_subleadlep")
            save_histogram_data(directory_path, data['mljj_subleadlep_emujj_400mll'])
            mass_tuples.append((directory_path, data['mljj_subleadlep_emujj_400mll']))

    return mass_tuples

def save_tuples(all_tuples, out_mass, client):
    output_dir = "root_outputs/masses/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{out_mass}")

    with uproot.recreate(output_file) as root_file:
        mass_tuples = save_data_to_directories(all_tuples)
        
        print("\nComputing mass tuples...")
        with ProgressBar():
            (masses,) = dask.compute(mass_tuples)

        print("masses", masses)
        branch_data = {}
        for name, mtuple in masses:
            if name not in branch_data:
                branch_data[name] = []
            branch_data[name].extend(mtuple)

        grouped_data = {}
        for name, values in branch_data.items():
            prefix = '/'.join(name.split('/')[:-1])
            if prefix not in grouped_data:
                grouped_data[prefix] = []
            grouped_data[prefix].append((name, values))

        for prefix, items in grouped_data.items():
            group_branch_data = {name: values for name, values in items}
            stripped_group_branch_data = {name.split('/')[-1]: values for name, values in group_branch_data.items()}
            branch_types = {name: np.array(values).dtype for name, values in stripped_group_branch_data.items()}
            ttree_path = f"{prefix}/masses"
            tree = root_file.mktree(ttree_path, branch_types)
            tree.extend({name: values for name, values in stripped_group_branch_data.items()})

    print(f"Mass tuples saved to {output_file}.")

