#!/bin/bash
set -o nounset
set -o pipefail

# ERA options available in the script
ERA_OPTIONS=(
  RunIISummer20UL18
  Run3Summer22
)

# Data options for Run3Summer22
DATA22_OPTIONS=(
  Run2022C_Muon
  Run2022D_Muon
  Run2022C_EGamma
  Run2022D_EGamma
)

# Data options for RunIISummer20UL18
DATA18_OPTIONS=(
  Run2018A_SingleMuon
  Run2018B_SingleMuon
  Run2018C_SingleMuon
  Run2018D_SingleMuon
  Run2018A_EGamma
  Run2018B_EGamma
  Run2018C_EGamma
  Run2018D_EGamma
)

# MC options (for all eras)
MC_OPTIONS=(
  DYJets
  TTbar
  tW
  WJets
  TTbarSemileptonic
  SingleTop
  TTX
  Diboson
  Triboson
)

# Validate mandatory mode argument: must be "data" or "bkg"
if [ "$#" -lt 1 ]; then
  echo "Usage: $0 {data|bkg} [era]"
  exit 1
fi

MODE="$1"
if [ "${MODE}" != "data" ] && [ "${MODE}" != "bkg" ]; then
  echo "Error: First argument must be either 'data' or 'bkg'"
  exit 1
fi

# Optional era argument: if provided, only that era is run
SELECTED_ERA=""
if [ "$#" -ge 2 ]; then
  SELECTED_ERA="$2"
  valid=false
  for era in "${ERA_OPTIONS[@]}"; do
    if [ "${era}" == "${SELECTED_ERA}" ]; then
      valid=true
      break
    fi
  done
  if [ "${valid}" != "true" ]; then
    echo "Error: Unknown era '${SELECTED_ERA}'. Valid options: ${ERA_OPTIONS[*]}"
    exit 1
  fi
  echo "Selected era: ${SELECTED_ERA}"
fi

# Function to run the analysis for a given era and process
run_analysis() {
  local era="$1"
  local process="$2"
  echo "Running analysis for era ${era} and --process ${process}"
  python3 bin/run_analysis.py "${era}" "${process}" --hists --skimmed || {
    echo "Error running analysis for process ${process} with era ${era}. Skipping..."
    return 1
  }
}

# Loop over each era and run the corresponding analyses based on the mode
for era in "${ERA_OPTIONS[@]}"; do
  # Skip eras not matching the selected era (if one was provided)
  if [ -n "${SELECTED_ERA}" ] && [ "${era}" != "${SELECTED_ERA}" ]; then
    continue
  fi

  echo "Starting analyses for era: ${era}"
  
  if [ "${MODE}" == "data" ]; then
    if [ "${era}" == "Run3Summer22" ]; then
      for process in "${DATA22_OPTIONS[@]}"; do
        run_analysis "${era}" "${process}"
      done
    elif [ "${era}" == "RunIISummer20UL18" ]; then
      for process in "${DATA18_OPTIONS[@]}"; do
        run_analysis "${era}" "${process}"
      done
    fi
  elif [ "${MODE}" == "bkg" ]; then
    for process in "${MC_OPTIONS[@]}"; do
      run_analysis "${era}" "${process}"
    done
  fi
done

echo "All analyses complete!"
