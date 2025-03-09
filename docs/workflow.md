# Full Workflow

## Table of Contents
1. [Cross-section Computation](xsec.md) – How to compute the cross-section of MC samples.
---

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

### Skim Events

* Once the preprocessed `JSON` file is created, we then use it to skim the files. Skimming/Slimming consists of removing unneccesary branches and events from the `ROOT` files, drastically reducing their size. To skim, one runs the bash script,
```
./Run3Summer23BPix_skims.sh
```
The output `ROOT` files are stored in the `test/Run3Summer23BPix` folder. There will be many skimmed files, which we can combine into one or two larger files (1-2 GB) with `ROOT`'s `hadd` command. Load `ROOT` with the LCG release:
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_106/x86_64-el9-gcc13-opt/setup.sh
```
Combine the files with
```
for i in {1..197}; do hadd DYto2L-4Jets_MLL-50to120_HT-40to70_skim${i}.root DYto2L-4Jets_MLL-50to120_HT-40to70_skim${i}-part*.root && rm DYto2L-4Jets_MLL-50to120_HT-40to70_skim${i}-part*.root; done
```
and
```
hadd DYto2L-4Jets_MLL-50to120_HT-40to70_skims1to197.root DYto2L-4Jets_MLL-50to120_HT-40to70_skim{1..197}.root && rm DYto2L-4Jets_MLL-50to120_HT-40to70_skim{1..197}.root
```
The output is a `ROOT` file, `DYto2L-4Jets_MLL-50to120_HT-40to70_skims1to197.root`, which contains all of the skimmed events. 

Lastly, upload the skimmed dataset to the LPC EOS using
```
xrdcp -r DYto2L-4Jets_MLL-50to120_HT-40to70 root://cmseos.fnal.gov//store/user/wijackso/WRAnalyzer/Skim_Tree_Lepton_Pt45/Run3Summer23BPix
```
Repeat this process for each dataset. To view the EOS storage system, use
```
eosls -lh store/user/wijackso/WRAnalyzer/Skim_Tree_Lepton_Pt45/Run3Summer23BPix
```
