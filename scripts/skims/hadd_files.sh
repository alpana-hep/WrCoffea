#!/bin/bash

source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh

# Ensure an argument is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <dataset_name>"
    exit 1
fi

# Get the dataset name from the argument
DATASET_NAME="$1"

echo "-------------------------------------------"
echo "Processing tarballs in: $(pwd)"
echo "-------------------------------------------"

# Extract all tarballs
for TAR_FILE in "${DATASET_NAME}"_*.tar.gz; do
    echo "Extracting: $TAR_FILE"
    tar -xzf "$TAR_FILE"
done

cd "$DATASET_NAME"

TOTAL_EVENTS=0
MERGED_FILE_COUNT=0
EVENT_THRESHOLD=400000  # Max events per merged file
CURRENT_EVENT_COUNT=0
MERGE_LIST=()

echo "-------------------------------------------"
echo "Counting events in each ROOT file..."
echo "-------------------------------------------"

# Get all ROOT files and sort by name
ROOT_FILES=($(ls *.root | sort))

for ROOT_FILE in "${ROOT_FILES[@]}"; do
    if [[ -f "$ROOT_FILE" ]]; then
        # Count the number of events
        EVENTS=$(root -l -b -q -e "TFile f(\"$ROOT_FILE\"); TTree *t = (TTree*)f.Get(\"Events\"); if (t) { cout << t->GetEntries() << endl; } else { cout << 0 << endl; }" 2>/dev/null)

        # If adding this file would exceed the limit, merge current files first
        if [[ $((CURRENT_EVENT_COUNT + EVENTS)) -gt $EVENT_THRESHOLD ]]; then
            if [[ ${#MERGE_LIST[@]} -gt 0 ]]; then
                MERGED_FILE="${DATASET_NAME}_${CAMPAIGN}_skim${MERGED_FILE_COUNT}.root"
                echo "Merging into: $MERGED_FILE"
                hadd -f "$MERGED_FILE" "${MERGE_LIST[@]}"

                # Remove original files after merging
                echo "Deleting merged files..."
                rm -f "${MERGE_LIST[@]}"

                # Reset merge list and counters
                MERGE_LIST=()
                CURRENT_EVENT_COUNT=0
                ((MERGED_FILE_COUNT++))
            fi
        fi

        # Add the current file to the merge list
        MERGE_LIST+=("$ROOT_FILE")
        CURRENT_EVENT_COUNT=$((CURRENT_EVENT_COUNT + EVENTS))
        TOTAL_EVENTS=$((TOTAL_EVENTS + EVENTS))
    fi
done

# Merge any remaining files (last batch)
if [[ ${#MERGE_LIST[@]} -gt 0 ]]; then
    MERGED_FILE="${DATASET_NAME}_${CAMPAIGN}_skim${MERGED_FILE_COUNT}.root"
    echo "Merging leftovers into: $MERGED_FILE"
    hadd -f "$MERGED_FILE" "${MERGE_LIST[@]}"

    # Remove original files after merging
    echo "Deleting merged files..."
    rm -f "${MERGE_LIST[@]}"
fi

echo "-------------------------------------------"
echo "Total events processed: $TOTAL_EVENTS"
echo "Merged into $((MERGED_FILE_COUNT + 1)) files"
echo "Original files deleted."
echo "-------------------------------------------"

cd ..
rm *.tar.gz
