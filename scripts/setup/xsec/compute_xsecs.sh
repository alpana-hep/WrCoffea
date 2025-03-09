#!/bin/bash

# Check if directory argument is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <subdirectory>"
    exit 1
fi

# The subdirectory for the specific dataset
SUBDIR="$1"

# Determine run and year based on SUBDIR
if [[ "$SUBDIR" == *"16"* ]]; then
    RUN="RunII"
    YEAR="2016"
elif [[ "$SUBDIR" == *"17"* ]]; then
    RUN="RunII"
    YEAR="2017"
elif [[ "$SUBDIR" == *"18"* ]]; then
    RUN="RunII"
    YEAR="2018"
elif [[ "$SUBDIR" == *"22"* ]]; then
    RUN="Run3"
    YEAR="2022"
elif [[ "$SUBDIR" == *"23"* ]]; then
    RUN="Run3"
    YEAR="2023"
else
    echo "Error: Year not recognized in SUBDIR."
    exit 1
fi

BASE_DIR="/uscms/home/bjackson/nobackup/WrCoffea/scripts/setup/xsec"

CMSSW_BASE="/uscms/home/bjackson/nobackup/x_sections/CMSSW_14_1_3/src"
# Change to the directory containing the necessary scripts
cd "$CMSSW_BASE" || { echo "Failed to change directory to $CMSSW_BASE"; exit 1; }

cmsenv

# Full path to the directory containing the input text files
DATA_DIR="/uscms/home/bjackson/nobackup/WrCoffea/data/xsec/miniaod/$RUN/$YEAR/$SUBDIR"

XSEC_DIR="/uscms/home/bjackson/nobackup/WrCoffea/data/xsec/$RUN/$YEAR/$SUBDIR"

# Check if the directory exists
if [ ! -d "$DATA_DIR" ]; then
    echo "Directory not found: $DATA_DIR"
    exit 1
fi

# Ensure XSEC_DIR exists
mkdir -p "$XSEC_DIR"

# Get the total number of .txt files
total_files=$(ls "$DATA_DIR"/*.txt | wc -l)

# Ensure there are files to process
if [ "$total_files" -eq 0 ]; then
    echo "No .txt files found in the directory: $DATA_DIR"
    exit 1
fi

# Initialize counter
counter=1

# Record the start time for the entire script
script_start_time=$(date +%s)

# Maximum number of retries for cmsRun
max_retries=10
retry_delay=10  # Delay (in seconds) before retrying

# Loop over all .txt files in the data directory
for file in "$DATA_DIR"/*.txt; do
    # Extract the base filename (remove directory path)
    base_name=$(basename "$file")
    
    # Remove _MINIAOD_files.txt suffix
    base_name="${base_name%_MINIAOD_files.txt}"

    # Define the log file name in the XSEC directory
    log_file="$XSEC_DIR/${base_name}_${SUBDIR}.log"

    # Record the start time for this iteration in seconds since the epoch
    start_time=$(date +%s)

    # Print the current file being processed with the counter
    echo "Processing file $counter/$total_files: $file"
    # Retry logic for cmsRun
    attempt=0
    while [ $attempt -lt $max_retries ]; do
        ((attempt++))
        echo "Attempt $attempt of $max_retries for $file"
        
        # Run the cmsRun command
        cmsRun "ana.py" inputFiles="$file" maxEvents=10000 > "$log_file" 2>&1
        cmsRun_exit_code=$?

        if [ $cmsRun_exit_code -eq 0 ]; then
            echo "cmsRun completed successfully for $file"
            break
        else
            echo "Error: cmsRun failed for $file (attempt $attempt of $max_retries)"
        fi

        # If we've exhausted retries, exit with failure
        if [ $attempt -eq $max_retries ]; then
            echo "Failed after $max_retries attempts. Exiting."
            exit 1
        fi

        # Wait before retrying
        echo "Retrying in $retry_delay seconds..."
        sleep $retry_delay
    done

    
    # Run the save_xsec.py script on the generated log file
    python3 "$BASE_DIR/save_xsec.py" "$SUBDIR" "$log_file"

    # Record the end time for this iteration in seconds since the epoch
    end_time=$(date +%s)

    # Calculate the duration of the loop
    duration=$((end_time - start_time))

    # Convert duration to minutes and seconds
    minutes=$((duration / 60))
    seconds=$((duration % 60))

    # Print the time it took for this iteration
    echo "Completed in: $minutes minutes and $seconds seconds"

    # Increment the counter
    counter=$((counter + 1))

    echo "----------------------------------------"
done

# Record the end time for the entire script
script_end_time=$(date +%s)

# Calculate the total duration for the entire script
script_duration=$((script_end_time - script_start_time))

# Convert total duration to minutes and seconds
script_minutes=$((script_duration / 60))
script_seconds=$((script_duration % 60))

# Print the total time taken for the entire script
echo "Total time for script execution: $script_minutes minutes and $script_seconds seconds"
