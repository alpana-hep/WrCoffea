import uproot
import os
import dask
from dask.diagnostics import ProgressBar
import numpy as np
def save_tuples(all_tuples):
    output_dir = "root_outputs/masses/"
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"example_masses.root")

    with uproot.recreate(output_file) as root_file:
        mass_tuples = []
        for process, data in all_tuples.items():
            for mass_name, mtuple in data["mass_dict"].items():
                mass_tuples.append((mass_name,mtuple))

        print("\nComputing mass tuples...")
        with ProgressBar():
            (masses,)= dask.compute(mass_tuples)

        branch_data = {}
        for name, mtuple in masses:
            if name not in branch_data:
                branch_data[name] = []
            branch_data[name].extend(mtuple)

        for process, data in all_tuples.items():
            mc = data['mc']
            process = data['process']
            directory_path = f"{mc}/{process}"
            ttree_path = f"{directory_path}/mass_tuples"
            branch_types = {}
            branch_types = {name: np.array(values).dtype for name, values in branch_data.items()}
            tree=root_file.mktree(f"{directory_path}/mass_tuples", branch_types)
            tree.extend({name: values for name, values in branch_data.items()})

    print(f"Mass tuples saved to {output_file}.")
