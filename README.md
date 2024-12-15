# WrCoffea

## Getting Started
Begin by cloning the repository,
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
Then source the appropriate LGC release. For example,
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-el9-gcc11-opt/setup.sh (LPC)
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos8-gcc11-opt/setup.sh (UMN)
```
Create and source a virtual python environment,
```
python3 -m venv coffea-cvfms-env
source coffea-cvfms-env/bin/activate
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
### Basic analysis
To run a basic analysis, 
```
python3 bin/run_analysis.py Run3Summer22 DYJets --hists --skimmed
```
More information can be found in the `README.md` file in other folders.

## Running at UMN
### Preprocess
To preprocess the background datasets (only needs to be done once),
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
python3.11 bin/run_analysis.py Run2Summer20UL18 DYJets --skimmed --umn --hists
```
where the sample can be either `DYJets` or `tt`.

To run over signal samples,
```
python3 bin/run_analysis.py Run2Autumn18 Signal --mass WR3200_N800 --umn --hists
```
where `--mass` can be `WR3200_N3000`, `WR3200_N1600`, `WR3200_N400` etc.

### Plotting
Plotting is handled in the `WR_Plotter` submodule,
```
cd WR_Plotter
```
