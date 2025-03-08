import uproot
import numpy as np
import sys
import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict

def get_branch_sizes(root_url, object_path):
    """Calculate the memory contribution of each branch in a remote ROOT file."""
    with uproot.open(root_url) as f:
        if object_path not in f:
            print(f"Warning: Object '{object_path}' not found in {root_url}")
            return None, None
#
        ttree = f[object_path]
        branch_sizes = {}
#
        for branch_name, branch in ttree.items():
            branch_array = branch.array(library="np")  # Load as NumPy array
            branch_size = branch_array.nbytes  # Memory usage in bytes
            branch_sizes[branch_name] = branch_size
#
        return branch_sizes, sum(branch_sizes.values())

#def get_branch_sizes(root_url, object_path):
#    """Calculate the memory contribution of each branch in a remote ROOT file."""
#    with uproot.open(root_url) as f:
#        if object_path not in f:
#            print(f"Warning: Object '{object_path}' not found in {root_url}")
#            return None, None

#        ttree = f[object_path]
#        branch_sizes = {}
#        total_uncompressed_size = 0

#        for branch_name, branch in ttree.items():
#            branch_size = branch.num_bytes  # Use ROOT's internal size estimate
#            branch_sizes[branch_name] = branch_size
#            total_uncompressed_size += branch_size

#        return branch_sizes, total_uncompressed_size

def group_branch_sizes(branch_sizes):
    """Group branch sizes by common prefixes (e.g., boostedTau_*, CorrT1METJet_*)."""
    grouped_sizes = defaultdict(int)

    for branch, size in branch_sizes.items():
        prefix = branch.split("_")[0]  # Get the prefix (first part of the branch name)
        grouped_sizes[prefix] += size  # Sum sizes of branches with the same prefix

    return grouped_sizes

def plot_pie_chart(grouped_sizes, total_size, root_url):
    """Create a pie chart showing branch contributions."""
    labels = []
    sizes = []
    other_size = 0

    # Separate major contributors and "other"
    for group, size in grouped_sizes.items():
        contribution = (size / total_size) * 100
        if contribution >= 1:
            labels.append(group)
            sizes.append(size)
        else:
            other_size += size

    if other_size > 0:
        labels.append("Other (<1%)")
        sizes.append(other_size)

    # Plot pie chart
    plt.figure(figsize=(8, 8))
    plt.pie(
        sizes, labels=labels, autopct="%1.1f%%", startangle=140, 
        colors=plt.cm.Paired.colors[:len(labels)], wedgeprops={"edgecolor": "black"}
    )
    plt.title(f"Memory Contribution by Branch Group\n{root_url}")
    plt.show()

def print_branch_contributions(grouped_sizes, total_size, root_url):
    """Prints grouped branch contributions to the total memory usage."""
    print(f"\nROOT File: {root_url}")
    print(f"Total branch memory usage: {total_size / 1024**2:.2f} MB\n")
    print(f"{'Branch Group':<40}{'Size (MB)':<15}{'Contribution (%)':<15}")
    print("-" * 70)

    for group, size in sorted(grouped_sizes.items(), key=lambda x: x[1], reverse=True):
        print(f"{group:<40}{size / 1024**2:<15.2f}{(size / total_size) * 100:<15.2f}")

def process_json(json_file):
    """Read JSON file and process each ROOT file."""
    with open(json_file, "r") as f:
        data = json.load(f)

    for dataset, dataset_info in data.items():
        print(f"\nProcessing dataset: {dataset}")
        if "files" not in dataset_info:
            print("Warning: No 'files' key found.")
            continue

        for root_url, file_info in dataset_info["files"].items():
            object_path = file_info.get("object_path", "Events")  # Default to "Events"
            branch_sizes, total_size = get_branch_sizes(root_url, object_path)

            if branch_sizes:
                grouped_sizes = group_branch_sizes(branch_sizes)
                print_branch_contributions(grouped_sizes, total_size, root_url)
                plot_pie_chart(grouped_sizes, total_size, root_url)  # Generate Pie Chart

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <json_file>")
        sys.exit(1)

    json_file = sys.argv[1]

    if not os.path.exists(json_file):
        print(f"Error: JSON file '{json_file}' not found.")
        sys.exit(1)

    process_json(json_file)
