import json
import argparse

def extract_wr_n(key):
    """
    Extracts WR and N values from the key for sorting.
    """
    wr_n_part = key.split("WR")[-1]
    wr, n = wr_n_part.split("_N")
    return int(wr), int(n)

def sort_json_by_wr_n(input_file, output_file):
    """
    Reads a JSON file, sorts its keys by WR and N values, and writes the sorted JSON to an output file.

    Parameters:
    - input_file: Path to the input JSON file.
    - output_file: Path to save the sorted JSON file.
    """
    # Load the JSON data
    with open(input_file, 'r') as file:
        data = json.load(file)

    # Sort the dictionary keys based on WR and N
    sorted_keys = sorted(data.keys(), key=extract_wr_n)

    # Reorder the dictionary
    sorted_data = {key: data[key] for key in sorted_keys}

    # Save the sorted dictionary back to a JSON file
    with open(output_file, 'w') as file:
        json.dump(sorted_data, file, indent=4)
    print(f"Sorted JSON saved to {output_file}")

if __name__ == "__main__":
    # Argument parser setup
    parser = argparse.ArgumentParser(description="Sort a JSON file by WR and N values in keys.")
    parser.add_argument("input_file", type=str, help="Path to the input JSON file")
    parser.add_argument("output_file", type=str, help="Path to save the sorted JSON file")
    args = parser.parse_args()

    # Sort the JSON and save the result
    sort_json_by_wr_n(args.input_file, args.output_file)
