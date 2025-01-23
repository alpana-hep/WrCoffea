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

* The files [bin/run_analysis.py](https://github.com/UMN-CMS/WrCoffea/blob/main/bin/run_analysis.py) and [src/analyzer.py](https://github.com/UMN-CMS/WrCoffea/blob/main/src/analyzer.py) make a standard selection and standard set of histograms. Independent studies where the variables, selections, histograms etc may differ are developed in the [tests](https://github.com/UMN-CMS/WrCoffea/tree/main/test) folder. It is usually easiest to copy the files and start from there. Once finished, new studies can integrated into the main pipeline via the `bin` or `python` or `src` folders.

## Full Workflow

* The following offers more detail on how to add a new MC campaign to the analyzer by way of example. 

### Cross-section Computation
#### Find MINIAOD files
* Create a `.txt` file with MINIAOD DAS dataset names in the directory `data/miniaod`. For example, see [data/miniaod/Run3Summer23BPix_datasets.txt](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/miniaod/Run3Summer23BPix_datasets.txt)
* Run the script [scripts/miniaod_files_for_xsec.py](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/scripts/miniaod_files_for_xsec.py). This takes in these dataset names, quieries DAS, and makes `.txt` files containing individual file paths for each dataset.
```
cd scripts
python3 miniaod_files_for_xsec.py Run3Summer23BPix
```
* The output `.txt` files are saved in `data/miniaod/Run3Summer23BPix`. For example, see [data/miniaod/Run3Summer23BPix/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_MINIAOD_files.txt](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/miniaod/Run3Summer23BPix/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_MINIAOD_files.txt).

#### Compute the cross-section
*To compute the cross section go a `cmssw` environment,
```
cd /uscms/home/bjackson/nobackup/x_sections/CMSSW_14_1_3/src
cmsenv
```
* Input the filelist as an argument to `ana.py`,
```
cmsRun ana.py inputFiles=/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/Run3Summer23BPix/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8_MINIAOD_files.txt maxEvents=10000000
```
* After the computing, a table will be outputted in the format
```
------------------------------------
GenXsecAnalyzer:
------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Overall cross-section summary 
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Process		xsec_before [pb]		passed	nposw	nnegw	tried	nposw	nnegw 	xsec_match [pb]			accepted [%]	 event_eff [%]
0		3.623e+02 +/- 2.332e-02		1176145	1176145	0	2467321	2467321	0	1.727e+02 +/- 1.157e-01		47.7 +/- 0.0	47.7 +/- 0.0
1		7.543e+02 +/- 3.174e-02		916149	916149	0	5086882	5086882	0	1.359e+02 +/- 1.286e-01		18.0 +/- 0.0	18.0 +/- 0.0
2		3.613e+02 +/- 1.408e-02		55609	55609	0	2462535	2462535	0	8.158e+00 +/- 3.421e-02		2.3 +/- 0.0	2.3 +/- 0.0
3		4.125e+01 +/- 2.653e-03		566	566	0	280218	280218	0	8.332e-02 +/- 3.499e-03		0.2 +/- 0.0	0.2 +/- 0.0
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Total		1.519e+03 +/- 4.191e-02		2148469	2148469	0	10296956	10296956	0	3.170e+02 +/- 1.926e-01		20.9 +/- 0.0	20.9 +/- 0.0
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Before matching: total cross section = 1.519e+03 +- 4.191e-02 pb
After matching: total cross section = 3.170e+02 +- 1.926e-01 pb
Matching efficiency = 0.2 +/- 0.0   [TO BE USED IN MCM]
Filter efficiency (taking into account weights)= (1.52064e+09) / (1.52064e+09) = 1.000e+00 +- 0.000e+00
Filter efficiency (event-level)= (1.00101e+06) / (1.00101e+06) = 1.000e+00 +- 0.000e+00    [TO BE USED IN MCM]

After filter: final cross section = 3.170e+02 +- 1.926e-01 pb
After filter: final fraction of events with negative weights = 0.000e+00 +- 0.000e+00
After filter: final equivalent lumi for 1M events (1/fb) = 3.155e+00 +- 3.691e-03
```
* The cross section to be used is `After filter: final cross section = 3.170e+02 +- 1.926e-01 pb`

#### Save the cross-section log file 

* Save the above output to a `.log` file in `data/x-secs/Run3Summer23BPix`. For example, see [data/x-secs/Run3Summer23BPix
/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8.log](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/x-secs/Run3Summer23BPix/TTto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8.log).

### Create JSON configuration files

#### Make a template JSON file

* Create a template `.JSON` file in the foler `data/configs/Run3Summer23BPix`. This file contains the each [DAS](https://cmsweb.cern.ch/das/) dataset name, with metadata indicating the MC campaign, process, dataset, and cross-section. Input the cross-section from the previous section. Note that the sum of the weights should be `0.0` in this file. For example, see [data/configs/Run3Summer23BPix
/Run3Summer23BPix_bkg_template.json](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/configs/Run3Summer23BPix/Run3Summer23BPix_bkg_template.json)

#### Compute the Sum of the Event Weights

* To compute the sum of the weights, run the script
```
python3 scripts/make_config.py Run3Summer23BPix bkg
```
* This script takes in the `JSON` template file, computes the sum of the event weights (which needs to be tracked if the datasets are to be skimmed), and outputs the same `JSON` file with the sum of the weights included. For example, see [data/configs/Run3Summer23BPix
/Run3Summer23BPix_bkg_cfg.json](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/configs/Run3Summer23BPix/Run3Summer23BPix_bkg_cfg.json)

### Preprocess Events

* The next step is to preprocess events, which takes in the `JSON` configuration file from above and uses Coffeas' built in DataDiscoveryCLI class to create a list of all available file replicas. It then preprocesses them using Coffeas' preprocess function.
```
python3 scripts/preprocessed_json.py Run3Summer23BPix bkg
```
* The preprocessed file information is stored in an output `JSON` file in the directory `data/jsons`. This output `JSON` file can either then be given to the skimmer, or directly to the analyzer if skimming is not needed. For example, see [data/jsons/Run3Summer23BPix/Run3Summer23BPix_bkg_preprocessed.json](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/jsons/Run3Summer23BPix/Run3Summer23BPix_bkg_preprocessed.json)


