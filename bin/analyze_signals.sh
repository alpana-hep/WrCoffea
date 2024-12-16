#!/bin/bash

# List of --mass options
MASS_OPTIONS=(
  WR1200_N200 WR1200_N400 WR1200_N600 WR1200_N800 WR1200_N1100
  WR1600_N400 WR1600_N600 WR1600_N800 WR1600_N1200 WR1600_N1500
  WR2000_N400 WR2000_N800 WR2000_N1000 WR2000_N1400 WR2000_N1900
  WR2400_N600 WR2400_N800 WR2400_N1200 WR2400_N1800 WR2400_N2300
  WR2800_N600 WR2800_N1000 WR2800_N1400 WR2800_N2000 WR2800_N2700
  WR3200_N800 WR3200_N1200 WR3200_N1600 WR3200_N2400 WR3200_N3000
)

# Base command
BASE_COMMAND="python3 bin/run_analysis.py Run2Autumn18 Signal --hists"

# Loop over each --mass option and execute the command
for MASS in "${MASS_OPTIONS[@]}"; do
  echo "Running analysis for --mass $MASS"
  $BASE_COMMAND --mass "$MASS"
  if [ $? -ne 0 ]; then
    echo "Error running analysis for --mass $MASS. Skipping..."
    continue
  fi
done

echo "All analyses complete!"
