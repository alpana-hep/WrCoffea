# Running the analyzer

## Create filesets
The first step is to find the files that will be fed into the analyzer. This can either be skimmed files that are located at UMN and Billy's EOS LPC area, or unskimmed files that we will query with rucio and DAS. 

To create a fileset of unskimmed files, use a command of the form 
```
python3 scripts/full_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_mc_lo_dy.json --dataset TTbar
python3 scripts/full_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_signal.json --dataset Signal
python3 scripts/full_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_data.json --dataset EGamma
```
where `--dataset` can be `DYJets`, `TTbar`, `TW`, `WJets`, `SingleTop`, `TTbarSemileptonic`, `TTV`, `Diboson`, `Triboson` (for backgrounds), `Signal` (for signal files), or `EGamma` or `Muon` (for data). Note that this does not work if running at UMN, use the script below instead.

Creating a fileset from skims is very similar, except one does not need the `dataset` argument. For example,
```
python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_mc_lo_dy.json 
python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_data.json
python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_signal.json 
```
The outputted `json` file locates the skimmed nanoAOD files from Billy's EOS LPC area, and creates filesets from each dataset.

For running at UMN, add the `--umn` flag to create the fileset from the skims at UMN,
```
python3 scripts/skimmed_fileset.py --config data/configs/Run3/2022/Run3Summer22/Run3Summer22_data.json --umn
```

## Basic Analysis
### Analyzing background samples
To run a basic analysis on a background sample, specify the era (either `RunIISummer20UL18`, `Run3Summer22`, or `Run3Summer22EE`) and the sample. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 DYJets
python3 bin/run_analysis.py Run3Summer22 DYJets
python3 bin/run_analysis.py Run3Summer22EE DYJets
```
other backgrounds that can be analyzed are `TTbar`, `tW`, `WJets`, `SingleTop`, `TTbarSemileptonic`, `TTX`, `Diboson`, and `Triboson`.

By default the analyzer looks for the skimmed filesets, and the output histograms will be saved to
```
WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root.
WR_Plotter/rootfiles/Run3/2022/Run3Summer22/WRAnalyzer_DYJets.root.
```

### Analyzing signal samples
To analyze signal files, use the `--mass` flag with the desired signal point. For example,
```
python3 bin/run_analysis.py RunIISummer20UL18 Signal --mass WR3200_N3000
python3 bin/run_analysis.py Run2Summer22 Signal --mass WR8000_N7900
```
Possible signal points can be found in the `data/` folder.

### Analyzing data samples
To analyze data, use a similar format
```
python3 bin/run_analysis.py RunIISummer20UL18 EGamma
python3 bin/run_analysis.py Run3Summer22EE Muon
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
python3 bin/run_analysis.py Run3Summer22 DYJets --name dr1p5
```
This will save the file 
```
WR_Plotter/rootfiles/Run3/2022/Run3Summer22/WRAnalyzer_dr1p5_DYJets.root.
```
Of course, both flags can be used,
```
python3 bin/run_analysis.py Run3Summer22EE DYJets --dir 3jets --name dr1p5
```
This will save the file
```
WR_Plotter/rootfiles/Run3/2022/Run3Summer22EE/3jets/WRAnalyzer_dr1p5_DYJets.root.
```

#### `--debug`
When making changes to the analyzer, one may want to run the analyzer without saving histograms. This can be done with,
```
python3 bin/run_analysis.py Run3Summer22EE DYJets --debug
```

#### `--reweight`
If one wishes to reweight a particular sample, use 
```
python3 bin/run_analysis.py Run3Summer22EE DYJets --reweight reweight_file.json
```
where `reweight_file.json` is the output file of scripts/derive_reweights.py

#### `--unskimmed`
If one wishes to run over the entire unskimmed files, use  
```
python3 bin/run_analysis.py Run3Summer22EE DYJets --unskimmed
```
This will tell the analyzer to find the unskimmed filesets instead.

#### `--condor`
If one wishes to run on condor on the LPC, use
```
python3 bin/run_analysis.py Run3Summer22EE DYJets --condor
```
More information can be found in the `README.md` file in other folders.

## Analyzing all
To analyzer all backgrounds in one command, execute the script
```
./bin/analyze_all.sh bkg RunIISummer20UL18
```
To analyze all signal samples
```
./bin/analyze_all.sh signal Run3Summer22
```
Or to analyze both `EGamma` and `Muon`,
```
./bin/analyze_all.sh data Run3Summer22EE
```
Similar to above, one can also specifcy `--dir` and `--name` to save files to specific directories and filenames. For example,
```
./bin/analyze_all.sh bkg RunIISummer20UL18 --dir 3jets --name dr1p5
```
