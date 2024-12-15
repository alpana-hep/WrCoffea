# LPC

## Introduction
*	**Purpose**: Holds miscellaneous scripts, often used for automation, running the pipeline, or post-processing.
*	**Content**: These might be shell scripts (.sh), Python scripts, or other scripts that automate tasks like running simulations, executing analysis workflows, downloading datasets, cleaning data, generating plots, etc. They are often used to orchestrate the different stages of the analysis pipeline.

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
