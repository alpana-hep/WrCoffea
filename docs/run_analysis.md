# Running the analyzer
## Basic Analysis
### Analyzing background samples
To run a basic analysis on background sample, specify the era (either `RunIISummer20UL18` or `Run3Summer22`) and the sample. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets
```
other backgrounds that can be ran on are `TTbar`, `tW`, `WJets`, `SingleTop`, `TTbarSemileptonic`, `TTX`, `Diboson`, and `Triboson`.

By default, the output histograms will be saved to
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root.
```

To analyzer all backgrounds in one command, execute the script
```
./bin/run_analyzer.sh bkg RunIISummer20UL18
```

### Analyzing signal samples
To analyze signal files, use the `--mass` flag with the desired signal point. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 Signal --mass WR3200_N3000
```
Note that signal files currently exist for `RunIISummer20UL18`

### Analyzing signal samples
To analyze data,
```
python3 bin/run_analysis.py RunIISummer20UL18 EGamma
```
where `EGamma` can also be replaced with `Muon`.

To analyze both `EGamma` and `Muon` in one command,
```
./bin/run_analyzer.sh data RunIISummer20UL18
```

## Optional Arguments

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

## Preprocessing
To preprocess the background datasets (needs to be done if a file in `configs/` is updated),
```
python3 scripts/make_skimmed_json.py Run2Summer20UL18 bkg --umn
```
where `Run2Summer20UL18` can be replaced with `Run3Summer22` to preprocess Run3 datasets.

Signal samples can be preprocessed with,
```
python3 scripts/make_skimmed_json.py Run2Autumn18 sig --umn
```

