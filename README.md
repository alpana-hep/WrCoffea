# WrCoffea Documentation

Welcome to the WR analyzer. The following links contain documentation for how to run the analyzer and make histograms, as well as how to add new MC campaigns.

## Table of Contents
- [Running the Analyzer](docs/run_analysis.md) – How to execute `run_analysis.py`.
- [Workflow Overview](docs/workflow.md) – Overview of the full workflow from scratch.
- [Plotting](docs/plotting.md) – Documentation for plotting.
- [Code Structure](README.md#-code-structure) – How the repository is organized.
- [Getting Started](README.md#getting-started) – How the repository is organized.   
## 📂 code-structure
This repository follows a structured layout to separate executable scripts, core analysis logic, and supporting documentation.

### **📂 `bin/` – Executable Scripts**
This directory contains **high-level scripts** meant to be executed directly:
- `run_analysis.py` – The main script that orchestrates the analysis pipeline.

### **📂 `docs/` – Documentation**
Contains Markdown documentation files:
- `workflow.md` – Overview of the analysis process.
- `run_analysis.md` – How to run the analyzer.
- `save_hists.md` – Explanation of histogram processing.

### **📂 `src/` – Core Analysis Code**
Contains the main physics analysis scripts:
- `analyzer.py` – Core physics analysis logic.

### **📂 `scripts/` – Helper Scripts**
This directory contains supporting scripts that are **not executed directly** but are used in workflows:
- `save_hists.py` – Processes and saves histograms.

### **📂 `data/` (Optional) – Input/Output Data**
If your analysis relies on data files (e.g., ROOT files, CSVs), you can store them here.

### **📂 `python/` (Optional) – Reusable Modules**
If you have Python helper functions or physics utilities, store them here for easy importing:
- `data_utils.py` – Functions for handling data.
- `hist_utils.py` – Functions for managing histograms.

### **📂 `test/` (Optional) – Unit Testing**
If you add automated tests, place them here using `pytest` or another framework.

## Getting Started
Begin by cloning the repository,
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
Create and source a virtual python environment,
```
python3 -m venv wr-env
source wr-env/bin/activate
```
Install the appropriate packages,
```
python3 -m pip install -r requirements.txt
```

### Grid UI
To set up a grid UI
```
voms-proxy-init --rfc --voms cms -valid 192:00
```
### ROOT
To use ROOT, source the appriopriate LGC release. 
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```
or at UMN,
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos8-gcc11-opt/setup.sh
```
### Extending the Analyzer

* The files [bin/run_analysis.py](https://github.com/UMN-CMS/WrCoffea/blob/main/bin/run_analysis.py) and [src/analyzer.py](https://github.com/UMN-CMS/WrCoffea/blob/main/src/analyzer.py) make a standard selection and standard set of histograms. Independent studies where the variables, selections, histograms etc may differ are developed in the [tests](https://github.com/UMN-CMS/WrCoffea/tree/main/test) folder. It is usually easiest to copy the files and start from there. Once finished, new studies can integrated into the main pipeline via the `bin` or `python` or `src` folders.
