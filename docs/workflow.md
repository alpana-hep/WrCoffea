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
