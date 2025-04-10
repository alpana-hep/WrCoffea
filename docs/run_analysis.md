# Running the analyzer
## Basic Analysis
### Analyzing background samples
To run a basic analysis on a background sample, specify the era (either `RunIISummer20UL18` or `Run3Summer22`) and the sample. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets
```
other backgrounds that can be analyzed are `TTbar`, `tW`, `WJets`, `SingleTop`, `TTbarSemileptonic`, `TTX`, `Diboson`, and `Triboson`.

By default, the output histograms will be saved to
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root.
```
### Analyzing signal samples
To analyze signal files, use the `--mass` flag with the desired signal point. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 Signal --mass WR3200_N3000
```
Note that signal files currently only exist for `RunIISummer20UL18`.

### Analyzing data samples
To analyze data,
```
python3 bin/run_analysis.py RunIISummer20UL18 EGamma
```
where `EGamma` can also be replaced with `Muon`.


## Optional Arguments

#### `--dir`
One can further specify a directory to save to with the  `--dir` flag. For example, 
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets --dir 3jets
```
This will save the file to 
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/3jets/WRAnalyzer_DYJets.root.
```

#### `--name`
Filenames can be modified with the `--name` flag. For instance,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets --name dr1p5
```
This will save the file 
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_dr1p5_DYJets.root.
```
Of course, both flags can be used,
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

## Analyzing all
To analyzer all backgrounds in one command, execute the script
```
./bin/analyze_all.sh bkg RunIISummer20UL18
```
To analyze all signal samples (n.b. this only works for `RunIISummer20UL18`),
```
./bin/analyze_all.sh signal RunIISummer20UL18
```
Or to analyze both `EGamma` and `Muon`,
```
./bin/analyze_all.sh data RunIISummer20UL18
```
Similar to above, one can also specifcy `--dir` and `--name` to save files to specific directories and filenames. For example,
```
./bin/analyze_all.sh bkg RunIISummer20UL18 --dir 3jets --name dr1p5
```

## Preprocessing
To preprocess the background datasets (needs to be done if a file in `configs/` is updated),
```
python3 scripts/make_skimmed_json.py RunIISummer20UL18 mc --umn
```
where `RunIISummer20UL18` can be replaced with `Run3Summer22` to preprocess Run3 datasets.

Signal samples can be preprocessed with,
```
python3 scripts/make_skimmed_json.py Run2Autumn18 sig --umn
```

