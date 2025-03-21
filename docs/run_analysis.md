## Running the analyzer

### Analyzing background
To run a basic analysis, 
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets
```
By default, the output histograms will be saved to
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root.
```
### Analyzing signal
To analyze signal files, use the `--mass` flag with the desired signal point. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 Signal --mass WR3200_N3000
```
### Optional Arguments

#### `--dir`
One can further specify a directory to save to with the  `--dir` flag. For example, 
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets --dir 3jets
```
this will save the files to 
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/3jets/WRAnalyzer_DYJets.root.
```

#### `--name`
The filenames can be modified with the `--name` flag. For instance,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets --name dr1p5
```
this will save the files to 
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_dr1p5_DYJets.root.
```
Or both flags can be used,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets --dir 3jets --name dr1p5
```
This will save the file
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/3jets/WRAnalyzer_dr1p5_DYJets.root.
```

#### `--debug`
When making changes to the analyzer, one may want to run the analyzer without saving histograms. This can be done with,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets --debug
```

More information can be found in the `README.md` file in other folders.

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
