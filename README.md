# WrCoffea

## Getting Started
Begin by cloning the repository,
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
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
To preprocess the datasets (only needs to be done once),
```
python3 scripts/make_skimmed_json.py Run2Summer20UL18 bkg --umn
```
where `Run2Summer20UL18` can be replaced with `Run3Summer22` to preprocess Run3 datasets.

### Basic analysis
To run a basic analysis at UMN, 
```
python3.11 bin/run_analysis.py Run2Summer20UL18 DYJets --skimmed --umn --hists
```

### Plotting
Plotting is handled in the `WR_Plotter` submodule,
```
cd WR_Plotter
```
