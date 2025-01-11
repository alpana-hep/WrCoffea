#!/bin/bash

# List of WR and N combinations (e.g., WR1200_N400, WR1500_N600, etc.)
DIRECTORIES=(
"WRtoNLtoLLJJ_WR1200_N400"
"WRtoNLtoLLJJ_WR1200_N800"
"WRtoNLtoLLJJ_WR1600_N1200"
"WRtoNLtoLLJJ_WR1600_N1500"
"WRtoNLtoLLJJ_WR1600_N400"
"WRtoNLtoLLJJ_WR1600_N600"
"WRtoNLtoLLJJ_WR1600_N800"
"WRtoNLtoLLJJ_WR2000_N1000"
"WRtoNLtoLLJJ_WR2000_N1400"
"WRtoNLtoLLJJ_WR2000_N1900"
"WRtoNLtoLLJJ_WR2000_N400"
"WRtoNLtoLLJJ_WR2000_N800"
"WRtoNLtoLLJJ_WR2400_N1200"
"WRtoNLtoLLJJ_WR2400_N1800"
"WRtoNLtoLLJJ_WR2400_N600"
"WRtoNLtoLLJJ_WR2400_N800"
"WRtoNLtoLLJJ_WR2800_N1000"
"WRtoNLtoLLJJ_WR2800_N1400"
"WRtoNLtoLLJJ_WR2800_N2000"
"WRtoNLtoLLJJ_WR2800_N2700"
"WRtoNLtoLLJJ_WR2800_N600"
"WRtoNLtoLLJJ_WR3200_N1200")

# Remote EOS path
EOS_PATH="root://cmseos.fnal.gov//store/user/wijackso/WRAnalyzer/Skim_Tree_Lepton_Pt45/Run2Autumn18"

for DIR in "${DIRECTORIES[@]}"; do
  if [ -d "$DIR" ]; then
    echo "Copying directory: $DIR to $EOS_PATH"
    
    # Use xrdcp to copy directory recursively
    xrdcp -r "$DIR" "$EOS_PATH"
    
    if [ $? -eq 0 ]; then
      echo "Successfully copied $DIR to $EOS_PATH"
    else
      echo "Error copying $DIR to $EOS_PATH"
    fi
  else
    echo "Directory not found: $DIR"
  fi
done
