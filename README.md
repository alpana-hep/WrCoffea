# WrCoffea

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

## Running the analyzer
### Each week if using LPC:
To set up a grid UI
```
voms-proxy-init --rfc --voms cms -valid 192:00
```
Source LGC release
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```
### Basic analysis
To run a basic analysis, 
```
python3 bin/run_analysis.py Run3Summer22 DYJets --hists --skimmed
```
More information can be found in the `README.md` file in other folders.

## Running at UMN
### Preprocess
To preprocess the background datasets (needs to be done if a file in `configs/` is updated),
```
python3 scripts/make_skimmed_json.py Run2Summer20UL18 bkg --umn
```
where `Run2Summer20UL18` can be replaced with `Run3Summer22` to preprocess Run3 datasets.

Signal samples can be preprocessed with,
```
python3 scripts/make_skimmed_json.py Run2Autumn18 sig --umn
```

### Basic analysis
To run a basic analysis at UMN, 
```
python3 bin/run_analysis.py Run2Summer20UL18 DYJets --skimmed --umn --hists
```
where the run is given by `Run2Summer20UL18` or `Run3Summer22`, and the process `DYJets` or `tt`.

To run over signal samples,
```
python3 bin/run_analysis.py Run2Autumn18 Signal --mass WR3200_N800 --umn --hists
```
where the possible signal points are given by [Run2Autumn18_mass_points.csv](https://github.com/UMN-CMS/WrCoffea/blob/main/data/Run2Autumn18_mass_points.csv)

### Plotting
Plotting is handled in the `WR_Plotter` submodule,
```
cd WR_Plotter
```

Source the appropriate LGC release. For example,
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos8-gcc11-opt/setup.sh
```

To plot a comparison of the Run2 vs. Run3 backgrounds,
```
python3 scripts/241120_Run2VSRun3/plot_CR.py --umn
```

To plot a comparison of the signal masses,
```
python3 scripts/241215_N3200_vs_N800/plot_SR.py --umn
```

### Extending the Analyzer

The files [bin/run_analysis.py](https://github.com/UMN-CMS/WrCoffea/blob/main/bin/run_analysis.py) and [src/analyzer.py](https://github.com/UMN-CMS/WrCoffea/blob/main/src/analyzer.py) make a standard selection and standard set of histograms. Independent studies where the variables, selections, histograms etc may differ are developed in the [tests](https://github.com/UMN-CMS/WrCoffea/tree/main/test) folder. It is usually easiest to copy the files and start from there. Once finished, new studies can integrated into the main pipeline via the `bin` or `python` or `src` folders.
