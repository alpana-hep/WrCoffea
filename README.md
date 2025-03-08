# WrCoffea Documentation

Welcome to the WR analyzer! This repository contains tools for analyzing and processing WR background, data and signal events. Below, you’ll find instructions on setting up the environment, running the analysis, and extending the framework.

## Table of Contents
- [Running the Analyzer](docs/run_analysis.md) – How to execute `run_analysis.py` to perform the analysis.
- [Workflow Overview](docs/workflow.md) – A detailed guide on the full data processing pipeline.
- [Plotting](docs/plotting.md) – Instructions for generating plots from the histogram ROOT files.
- [Code Structure](README.md#-code-structure) – Explanation of the repository organization.
- [Getting Started](README.md#getting-started) – Instructions for installing and setting up the analyzer.
---
## 📂 Repo Structure
This repository is structured to separate executable scripts, core analysis logic, and documentation.

```
bin/       # Contains the run_analysis.py script to execute the analysis.
docs/      # Documentation files
src/       # Contains main analyzer code
scripts/   # Helper scripts for pre- and post-processing
data/      # Input/output datasets
python/    # Reusable Python modules
test/      # Test and developmental scripts
```
---
## Getting Started
Begin by cloning the repository,
```bash
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
Create and source a virtual python environment,
```bash
python3 -m venv wr-env
source wr-env/bin/activate
```
Install the appropriate packages,
```bash
python3 -m pip install -r requirements.txt
```

### Grid UI
To authenticate for accessing grid resources, use:
```bash
voms-proxy-init --rfc --voms cms -valid 192:00
```

### ROOT
To enable ROOT functionality, source the appropriate LCG release:
```bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```
If using UMN’s setup, use:
```bash
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos8-gcc11-opt/setup.sh
```
---
## Extending the Analyzer
The files [bin/run_analysis.py](https://github.com/UMN-CMS/WrCoffea/blob/main/bin/run_analysis.py) and [src/analyzer.py](https://github.com/UMN-CMS/WrCoffea/blob/main/src/analyzer.py) define a standard event selection and histogramming process.

For independent studies with **custom variables, selections, or histograms**, develop your scripts in the [`test/`](https://github.com/UMN-CMS/WrCoffea/tree/main/test) folder.

### Adding a New Study
1. Copy an existing script from `test/`:
   ```bash
   cp src/analyzer.py test/dev_analyzer.py
   ```
2. Modify the script to include your custom selections and histograms.
3. Once finalized, integrate your study into the main pipeline via `bin/`, `python/`, or `src/`.
---
