#!/bin/bash

# Exit on error
set -euo pipefail

source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

# Ensure an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <dataset_name>"
    exit 1
fi

# Get the dataset name from the argument
DATASET_NAME="$1"

# Define the directory name
TARGET_DIR="$DATASET_NAME"

# Create the directory if it does not exist
mkdir -p "$TARGET_DIR"

# Move all matching tar.gz files into the directory
mv "${DATASET_NAME}"_*.tar.gz "$TARGET_DIR"

# Change to the directory
cd "$TARGET_DIR"

echo "-------------------------------------------"
echo "Processing tarballs in: $(pwd)"
echo "-------------------------------------------"

# Loop over all tar.gz files
for TAR_FILE in *.tar.gz; do
    echo "Extracting: $TAR_FILE"
    
    # Extract the tarball
    tar -xzf "$TAR_FILE"

    # Find all .root files in the extracted directory
    ROOT_FILES=$(find . -type f -name "*.root")

    # Define the output merged ROOT filename based on tarball name
    MERGED_FILE="${TAR_FILE%.tar.gz}.root"

    # Merge ROOT files using hadd (if there are any ROOT files)
    if [[ -n "$ROOT_FILES" ]]; then
        echo "Merging ROOT files into: $MERGED_FILE"
        hadd -f "$MERGED_FILE" $ROOT_FILES
        echo "✅ Merged successfully!"
    else
        echo "⚠️ No ROOT files found in $TAR_FILE"
    fi

    # Optional: Remove extracted files after merging to save space
    rm -rf "${TAR_FILE%.tar.gz}"
done

echo "-------------------------------------------"
echo "✅ All tarballs processed and merged!"
echo "-------------------------------------------"
