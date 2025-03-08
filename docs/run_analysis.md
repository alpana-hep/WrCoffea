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

To make histograms for all signal samples, use the script
```
./bin/analyze_signals.sh
```
which executes  `run_analysis.py` in a loop with all of the signal points.
