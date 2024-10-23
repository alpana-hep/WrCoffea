# Scripts

## Introduction
*	**Purpose**: Holds miscellaneous scripts, often used for automation, running the pipeline, or post-processing.
*	**Content**: These might be shell scripts (.sh), Python scripts, or other scripts that automate tasks like running simulations, executing analysis workflows, downloading datasets, cleaning data, generating plots, etc. They are often used to orchestrate the different stages of the analysis pipeline.

## Description of files
### [miniaod_files_for_x_sec.py](https://github.com/UMN-CMS/WrCoffea/blob/simplify/scripts/miniaod_files_for_xsec.py) 
#### Description
* Uses a list of MINIAOD [dataset names](https://github.com/UMN-CMS/WrCoffea/blob/simplify/data/miniaod_files/Run3Summer22/Run3Summer22_bkg_datasets.txt) to generate [filelists](https://github.com/UMN-CMS/WrCoffea/tree/simplify/data/miniaod_files/Run3Summer22) of MINIAOD `ROOT` files for each MC dataset. 

#### Example usage
```
python3 miniaod_files_for_xsec.py Run3Summer22 bkg
```
### [ana.py](https://github.com/UMN-CMS/WrCoffea/blob/simplify/scripts/ana.py)

#### Description
* Takes the lists created by `miniaod_files_for_x_sec.py` and combines the files to compute the cross section for the dataset (must be run in a `CMSSW` area). For more information see the [twiki](https://twiki.cern.ch/twiki/bin/viewauth/CMS/HowToGenXSecAnalyzer#Running_the_GenXSecAnalyzer_on_a).

#### Example usage
```
cmsRun ana.py inputFiles=/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod_files/Run3Summer22/DYto2L-4Jets_MLL-50to120_HT-40to70_TuneCP5_13p6TeV_madgraphMLM-pythia8_MINIAOD_files.txt maxEvents=-1
```
This generates a table of the following form, where `After filter: final cross section` is the final cross section stored in the `JSON` [configuration files](https://github.com/UMN-CMS/WrCoffea/blob/simplify/data/configs/Run3Summer22/Run3Summer22_bkg_cfg.json).
```------------------------------------
GenXsecAnalyzer:
------------------------------------
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Overall cross-section summary 
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Process		xsec_before [pb]		passed	nposw	nnegw	tried	nposw	nnegw 	xsec_match [pb]			accepted [%]	 event_eff [%]
0		3.622e+02 +/- 3.696e-03		47043383	47043383	0	98673166	98673166	0	1.727e+02 +/- 1.830e-02		47.7 +/- 0.0	47.7 +/- 0.0
1		7.541e+02 +/- 5.041e-03		36522573	36522573	0	203240575	203240575	0	1.355e+02 +/- 2.033e-02		18.0 +/- 0.0	18.0 +/- 0.0
2		3.613e+02 +/- 2.229e-03		2190020	2190020	0	98487994	98487994	0	8.033e+00 +/- 5.368e-03		2.2 +/- 0.0	2.2 +/- 0.0
3		4.127e+01 +/- 4.201e-04		22588	22588	0	11200884	11200884	0	8.323e-02 +/- 5.532e-04		0.2 +/- 0.0	0.2 +/- 0.0
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------- 
Total		1.519e+03 +/- 6.650e-03		85778564	85778564	0	411602619	411602619	0	3.165e+02 +/- 3.044e-02		20.8 +/- 0.0	20.8 +/- 0.0
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Before matching: total cross section = 1.519e+03 +- 6.650e-03 pb
After matching: total cross section = 3.165e+02 +- 3.044e-02 pb
Matching efficiency = 0.2 +/- 0.0   [TO BE USED IN MCM]
Filter efficiency (taking into account weights)= (6.17967e+10) / (6.17967e+10) = 1.000e+00 +- 0.000e+00
Filter efficiency (event-level)= (4.06867e+07) / (4.06867e+07) = 1.000e+00 +- 0.000e+00    [TO BE USED IN MCM]

After filter: final cross section = 3.165e+02 +- 3.044e-02 pb
After filter: final fraction of events with negative weights = 0.000e+00 +- 0.000e+00
After filter: final equivalent lumi for 1M events (1/fb) = 3.159e+00 +- 3.174e-03
```
### [preprocessed_json.py](https://github.com/UMN-CMS/WrCoffea/blob/simplify/scripts/ana.py)
#### Description
* Takes in a `JSON` [configuration file](https://github.com/UMN-CMS/WrCoffea/blob/simplify/data/configs/Run3Summer22/Run3Summer22_bkg_cfg.json) and uses Coffeas' built in `DataDiscoveryCLI` [class](https://github.com/CoffeaTeam/coffea/blob/master/src/coffea/dataset_tools/dataset_query.py#L109) to create a list of all available file replicas. It then preprocesses them using Coffeas' [preprocess function](https://github.com/CoffeaTeam/coffea/blob/master/src/coffea/dataset_tools/preprocess.py#L253) so that they can be skimmed, or given directly to the analyzer if skimming is not needed. This information is stored in an output `JSON` [file](https://github.com/UMN-CMS/WrCoffea/blob/simplify/data/jsons/Run3Summer22/Preprocessed/Run3Summer22_Bkg_Preprocessed.json). If the sample is MC, it also computes the sum of the event weights for each dataset.
#### Example usage
```
python3 preprocessed_json.py Run3Summer22 bkg
```
