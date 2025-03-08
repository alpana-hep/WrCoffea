# WrCoffea Documentation

Welcome to the WR analyzer. The following links contain documentation for how to run the analyzer and make histograms, as well as how to add new MC campaigns.

## Table of Contents
- [Running the Analyzer](docs/run_analysis.md) – How to execute `run_analysis.py`.
- [Workflow Overview](docs/workflow.md) – Overview of the full workflow from scratch.
- [Plotting](docs/plotting.md) – Documentation for plotting.
- [Code Structure](docs/#code-structure) – How the repository is organized.

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

### If using LPC:
To set up a grid UI
```
voms-proxy-init --rfc --voms cms -valid 192:00
```
To source the LGC release on LPC (e.g. to use a TBrowser)
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```
### UMN
To source the LGC release at UMN
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos8-gcc11-opt/setup.sh
```

### Extending the Analyzer

The files [bin/run_analysis.py](https://github.com/UMN-CMS/WrCoffea/blob/main/bin/run_analysis.py) and [src/analyzer.py](https://github.com/UMN-CMS/WrCoffea/blob/main/src/analyzer.py) make a standard selection and standard set of histograms. Independent studies where the variables, selections, histograms etc may differ are developed in the [tests](https://github.com/UMN-CMS/WrCoffea/tree/main/test) folder. It is usually easiest to copy the files and start from there. Once finished, new studies can integrated into the main pipeline via the `bin` or `python` or `src` folders.
