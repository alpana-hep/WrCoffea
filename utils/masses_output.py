import uproot
import os
import dask
from dask.diagnostics import ProgressBar
import numpy as np

def save_tuples(all_tuples, out_mass, client):
    output_dir = "root_outputs/masses/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{out_mass}")

    with uproot.recreate(output_file) as root_file:
        mass_tuples = []
        for process_path, data in all_tuples.items():
            directory_path = f"{data['mc']}{data['process']}/{data['dataset']}/"
            for mass_name, mtuple in data["mass_tuples"].items():
                mass_tuples.append((directory_path + mass_name, mtuple))

        print("\nComputing mass tuples...")
        with ProgressBar():
            (masses,) = dask.compute(mass_tuples)

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
