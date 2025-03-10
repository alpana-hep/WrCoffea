# Analysis Workflow

## Overview
*	This section contains a detailed description of the workflow. Most of the scripts in this folder require a grid certificate, or EOS LPC access etc and thus need to be run on the LPC.

## Introduction
*	The workflow starts in the `data/configs/Run2Summer20UL18` [folder](https://github.com/UMN-CMS/WrCoffea/tree/main/data/configs/Run2Summer20UL18):
```
cd /uscms/home/bjackson/nobackup/WrCoffea/data/configs/Run2Summer20UL18
```
*	In this folder is a user-provided file, [Run2Summer20UL18_bkg_template.json](https://github.com/UMN-CMS/WrCoffea/blob/main/data/configs/Run2Summer20UL18/Run2Summer20UL18_bkg_template.json). This template file contains the each [DAS](https://cmsweb.cern.ch/das/) dataset name, with metadata indicating the MC campaign, process, dataset, cross-section and the sum of the event weights of all of the events for a given dataset. The first step of the process is to compute the cross-section and sum of the weights for each dataset.

### Computing the cross-section
*	The cross-section is computed with [GenXSecAnalyzer](https://twiki.cern.ch/twiki/bin/viewauth/CMS/HowToGenXSecAnalyzer). It does this by taking in a list of MINIAOD filenames, and using [ana.py](https://github.com/UMN-CMS/WrCoffea/blob/main/scripts/ana.py) to compute the cross-section over all of the files.
* The MINIAOD DAS dataset names are provided by the user in the file [Run2Summer20UL18_bkg_datasets.txt](https://github.com/UMN-CMS/WrCoffea/blob/main/data/miniaod/Run2Summer20UL18/Run2Summer20UL18_bkg_datasets.txt)
* The script [miniaod_files_for_xsec.py](https://github.com/UMN-CMS/WrCoffea/blob/main/scripts/miniaod_files_for_xsec.py) takes in this list of datasets, quieries DAS and makes `.txt` files containing all of the file paths for each dataset. This is saved in the folder `/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/Run2Summer20UL18`. For example,
```
python3 miniaod_files_for_xsec.py Run2Summer20UL18
```
Then to compute the cross section,
```
cd /uscms/home/bjackson/nobackup/x_sections/CMSSW_14_1_3/src
cmsenv
```
And input the filelist as an argument to `ana.py`,
```
cmsRun ana.py inputFiles=/uscms/home/bjackson/nobackup/WrCoffea/data/miniaod/Run3Summer22/DYto2L-4Jets_MLL-50to120_HT-40to70_TuneCP5_13p6TeV_madgraphMLM-pythia8_MINIAOD_files.txt maxEvents=-1
```
After the computing, a table will be outputted in the format
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
The cross section to be used is `After filter: final cross section = 3.170e+02 +- 1.926e-01 pb`
## Description of files
A description and example use of each file in the `scripts/` directory is described below, in the order that they would be used to process a new MC campaign.

### [preprocessed_json.py](https://github.com/UMN-CMS/WrCoffea/blob/simplify/scripts/preprocessed_json.py)
#### Description
* Takes in a `JSON` [configuration file](https://github.com/UMN-CMS/WrCoffea/blob/simplify/data/configs/Run3Summer22/Run3Summer22_bkg_cfg.json) and uses Coffeas' built in `DataDiscoveryCLI` [class](https://github.com/CoffeaTeam/coffea/blob/master/src/coffea/dataset_tools/dataset_query.py#L109) to create a list of all available file replicas. It then preprocesses them using Coffeas' [preprocess function](https://github.com/CoffeaTeam/coffea/blob/master/src/coffea/dataset_tools/preprocess.py#L253) so that they can be skimmed, or given directly to the analyzer if skimming is not needed. This information is stored in an output `JSON` [file](https://github.com/UMN-CMS/WrCoffea/blob/simplify/data/jsons/Run3Summer22/Run3Summer22_Bkg_Preprocessed.json). If the sample is MC, it also computes the sum of the event weights for each dataset.
#### Example usage
```
python3 preprocessed_json.py Run3Summer22 bkg
```

### [skim_files.py](https://github.com/UMN-CMS/WrCoffea/blob/simplify/scripts/skim_files.py)
#### Description
* Takes in the `JSON` file produced by `preprocessed_json.py`, and skims the `ROOT` files for a given dataset. The skimmed files are saved to the [test](https://github.com/UMN-CMS/WrCoffea/tree/simplify/test) folder. 
* #### Example usage
```
python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-40to70 --start 1
```
* The script is actually run via a `bash' [script](https://github.com/UMN-CMS/WrCoffea/blob/simplify/scripts/Run3Summer22_skims.sh), which skims all files in all datasets for a given campaign,
```
./Run2Summer20UL18_skims.sh
```
* The skimmed files are saved locally, into a `tmp` folder. Before uploading them to EOS, they can be merged together. For example,
```
for i in {1..28}; do hadd DYJetsToLL_M-50_HT-400to600_skim${i}.root DYJetsToLL_M-50_HT-400to600_skim${i}-part*.root && rm DYJetsToLL_M-50_HT-400to600_skim${i}-part*.root; done
hadd DYJetsToLL_M-50_HT-400to600_skims1to14.root DYJetsToLL_M-50_HT-400to600_skim{1..14}.root && hadd DYJetsToLL_M-50_HT-400to600_skims15to28.root DYJetsToLL_M-50_HT-400to600_skim{15..28}.root && rm DYJetsToLL_M-50_HT-400to600_skim{1..28}.root
```
* To copy to EOS, go into the `tmp` folder and use a command of the form
```
xrdcp -r DYJetsToLL_M-50_HT-70to100 root://cmseos.fnal.gov//store/user/wijackso/skims/UL2018/lep_pt_45
```
