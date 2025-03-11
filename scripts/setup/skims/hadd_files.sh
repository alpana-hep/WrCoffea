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

echo "-------------------------------------------"
echo "Counting events and merging files..."
echo "-------------------------------------------"

# Initialize counters
TOTAL_EVENTS=0
MERGED_FILE_COUNT=0
EVENT_THRESHOLD=400000  # Max events per merged file
CURRENT_EVENT_COUNT=0
MERGE_LIST=()

# Get all ROOT files and sort by name
mapfile -t ROOT_FILES < <(ls *.root 2>/dev/null | sort)

# Declare an associative array to group files by skim number (only for SingleMuon/EGamma)
declare -A SKIM_GROUPS

# Step 1: Categorize files
for ROOT_FILE in "${ROOT_FILES[@]}"; do
    if [[ -f "$ROOT_FILE" ]]; then
        # Count events in this file
        EVENTS=$(root -l -b -q -e "TFile f(\"$ROOT_FILE\"); TTree *t = (TTree*)f.Get(\"Events\"); if (t) { cout << t->GetEntries() << endl; } else { cout << 0 << endl; }" 2>/dev/null)

	# Special handling for datasets containing "Muon" or "EGamma"
	if [[ "$DATASET_NAME" =~ Muon || "$DATASET_NAME" =~ EGamma ]]; then
	    if [[ "$ROOT_FILE" =~ skim([0-9]+)-part[0-9]+\.root ]]; then
		SKIM_NUM="${BASH_REMATCH[1]}"
		SKIM_GROUPS["$SKIM_NUM"]+="$ROOT_FILE "
	    fi
        else
            # Standard merging for other datasets
            if [[ $((CURRENT_EVENT_COUNT + EVENTS)) -gt $EVENT_THRESHOLD ]]; then
                if [[ ${#MERGE_LIST[@]} -gt 0 ]]; then
                    MERGED_FILE="${DATASET_NAME}_skim${MERGED_FILE_COUNT}.root"
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

            # Add file to merge list for standard datasets
            MERGE_LIST+=("$ROOT_FILE")
            CURRENT_EVENT_COUNT=$((CURRENT_EVENT_COUNT + EVENTS))
            TOTAL_EVENTS=$((TOTAL_EVENTS + EVENTS))
        fi
    fi
done

# Step 2: Merge remaining standard dataset files
if [[ ${#MERGE_LIST[@]} -gt 0 ]]; then
    MERGED_FILE="${DATASET_NAME}_skim${MERGED_FILE_COUNT}.root"
    echo "Merging leftovers into: $MERGED_FILE"
    hadd -f "$MERGED_FILE" "${MERGE_LIST[@]}"

    # Remove original files after merging
    echo "Deleting merged files..."
    rm -f "${MERGE_LIST[@]}"
fi

# Step 3: Merge SingleMuon & EGamma files by skim number
for SKIM_NUM in "${!SKIM_GROUPS[@]}"; do
    MERGE_LIST=(${SKIM_GROUPS["$SKIM_NUM"]})  # Convert space-separated string to array
    
    if [[ ${#MERGE_LIST[@]} -gt 0 ]]; then
        MERGED_FILE="${DATASET_NAME}_skim${SKIM_NUM}.root"
        echo "Merging skim $SKIM_NUM into: $MERGED_FILE"
        hadd -f "$MERGED_FILE" "${MERGE_LIST[@]}"

        # Remove original files after merging
        echo "Deleting merged files..."
        rm -f "${MERGE_LIST[@]}"
    fi
done

echo "-------------------------------------------"
echo "Total events processed: $TOTAL_EVENTS"
echo "Merged into $((MERGED_FILE_COUNT + ${#SKIM_GROUPS[@]})) files"
echo "Original files deleted."
echo "-------------------------------------------"

cd ..
rm *.tar.gz
