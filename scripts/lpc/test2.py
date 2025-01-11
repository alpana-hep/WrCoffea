import json

# The input JSON file
input_file = "Run2Autumn18_sig.json"
output_file = "filtered_ordered.json"

# Desired order of entries
desired_order = [
    "WRtoNLtoLLJJ_WR3200_N800",
    "WRtoNLtoLLJJ_WR1200_N1100",
    "WRtoNLtoLLJJ_WR1200_N600",
    "WRtoNLtoLLJJ_WR1200_N200",
    "WRtoNLtoLLJJ_WR2000_N1900",
    "WRtoNLtoLLJJ_WR2000_N1000",
    "WRtoNLtoLLJJ_WR2000_N400",
    "WRtoNLtoLLJJ_WR2800_N2700",
    "WRtoNLtoLLJJ_WR2800_N1400",
    "WRtoNLtoLLJJ_WR2800_N600",
    "WRtoNLtoLLJJ_WR1600_N1500",
    "WRtoNLtoLLJJ_WR1600_N800",
    "WRtoNLtoLLJJ_WR1600_N400",
    "WRtoNLtoLLJJ_WR2400_N2300",
    "WRtoNLtoLLJJ_WR2400_N1200",
    "WRtoNLtoLLJJ_WR2400_N600",
    "WRtoNLtoLLJJ_WR3200_N3000",
    "WRtoNLtoLLJJ_WR3200_N1600"
]

# Load the JSON data
with open(input_file, "r") as f:
    data = json.load(f)

# Create a new dictionary with only the desired entries in the specified order
filtered_data = {key: data[key] for key in desired_order if key in data}

# Save the filtered and ordered data to a new JSON file
with open(output_file, "w") as f:
    json.dump(filtered_data, f, indent=4)

print(f"Filtered and ordered data saved to {output_file}")
