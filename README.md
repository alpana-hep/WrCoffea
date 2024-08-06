# WrCoffea

## Getting Started
Begin by cloning the repository,
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
## Running the analyzer
### The first time
```
bash bootstrap.sh
```
The `./shell` executable can then be used to start an apptainer shell with a coffea environment. For more information: https://github.com/CoffeaTeam/lpcjobqueue

## Running over MC Samples
### Obtain replica MC files
First, `cd` into the `datasets` directory:
 ```
cd datasets
```
The first step is to use Coffeas' built in `DataDiscoveryCLI` class to simplify dataset query, and create a list of all available file replicas. The command to do this is:
```
python3 construct_bkg_fileset.py 2018
```
It takes one mandatory argument, which is the year of the background sample. In this case, `2018` corresponds to the 2018 Ultra Legacy campaign. The output is a json file, `UL2018_Bkg.json`, which is essentially a dictionary of replica files of all the background processes. It is stored in the `datasets/backgrounds` folder. For more information, see https://coffeateam.github.io/coffea/notebooks/dataset_discovery.html
### Preprocess MC files
The replicas metadata contain the file location in the CMS grid. This info can be preprocessed with uproot and dask-awkward to extract the fileset. Practically a fileset is a collection of metadata about the file location, file name, chunks splitting, that can be used directly to configure the uproot reading. The script to do this is also in the `datasets` directory:
```
python3 preprocess.py backgrounds/UL2018_Bkg
```
It takes a single argument, which is the path to the `json` file that was produced when constructing the background `json` replica files (however notice the `.json` extension is omitted). Two files are produced from this script, `UL2018_Bkg_preprocessed_all.json`, which is the fileset of all preprocessed files (successful or not), and `UL2018_Bkg_preprocessed_runnable.json`, which is the list of only the runnnable files. To see the differences between them (and hopefully there are none), run
```
diff backgrounds/UL2018_Bkg_preprocessed_runnable.json backgrounds/UL2018_Bkg_preprocessed_all.json
```
### Analyze MC files
The output of the preprocessing can be used directly to start an analysis with dask-awkward. This is done via the `run_analysis` script in the `WrCoffea` directory. To run the analyzer, a sample set and process must be specified as arguments. In general, the format is
```
python3 run_analysis.py <year> <process> --hists <output_filename>.root
```
For example, 
```
python3 run_analysis.py 2018 DYJets --hists DYJets.root
```
The options for background processes are `DYJets`, `tt+tW`, `tt_semileptonic`, `WJets`, `Diboson`, `Triboson`, `ttX`, `SingleTop`.

There are two additional optional arguments:

`--executor lpc`: Specify whether or not to run on the LPC. If this argument is used, one must first start an apptainer shell with a coffea environment by running `./shell coffeateam/coffea-dask-almalinux8:latest`.

`--masses`: Generate a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$).

Lastly, for debugging purposes one can also change the `max_chunks` and `max_files` parameters inside the `run_analysis.py` script to significantly shorten the analysis time. The `--hists` argument can also be omitted if no histograms are desired.

The output root file of histograms is stored in the `root_outputs/hists` directory.

## Running over Data
Running over data is slightly more complicated than MC samples because there is an additional skimming step required. The workflow is described below.

### Obtain replica Data files
Similar to MC, we first obtain the avaliable file replicas. The command to do this is:
```
cd datasets
python3 construct_data_fileset.py 2018
```
### Preprocess Data files
We then preprocess the data files:
```
python3 preprocess.py data/UL2018_Data
```
Check the differences between the preprocessed data files:
```
diff data/UL2018_Data_preprocessed_all.json data/UL2018_Data_preprocessed_runnable.json
```

### Skim Data files
To reduce the size of the data files we then skim them, which involves making a cut on the lepton pT of 45 GeV, and selecting only the branches needed in the analysis. The format of the data skimming script is:
```
python3 data_skim.py <dataset> <year> <run>
```
For example,
```
python3 data_skim.py SingleMuon 2018 RunA
```
However, the script currently has memory problems, so only a few data files can be skimmed at a time. As a temporary fix, run the script
```
./submit_jobs.sh
```
which will skim two files at a time without having to manually rerun the python script.

The output skimmed data root files are stored in the `dataskims/` directory. These should be moved to EOS at some point.

### Merge Data files
After the data files are skimmed, each one has about 70k events. To reduce the stress on Coffea when analyzing them, we them merge these files together, so each one has ~2 million events. To do this, we first `cd` to the directory where the skimmed files are. For example,
```
cd dataskims/SingleMuon2018RunAlepPt45
```
Then use ROOT's hadd command to merge ~30 files at a time together:
```
hadd SingleMuon2018RunA_part1-30.root SingleMuon2018RunA_file{1..30}-part0.root
rm SingleMuon2018RunA_file{1..30}-part0.root
```
### Construct fileset of skimmed data 
Once we have merged the skimmed data files, we need to contruct the json fileset of them. The command for this is in the `datasets/` directory:
```
python3 construct_skimmeddata_fileset.py
```
The skimmed filenames are hardcoded into `construct_skimmeddata_fileset.py`.

### Preprocess skimmed data
Similar to before, we then need to preprocess these files:
```
python3 preprocess.py dataskims/UL2018_skimmed_data
diff UL2018_skimmed_data_preprocessed_all.json UL2018_skimmed_data_preprocessed_runnable.json
```

### Analyze data files
The output of the preprocessing can be used directly to start an analysis with dask-awkward. This is done via the `run_analysis` script in the `WrCoffea` directory. To run the analyzer, a sample set and process must be specified as arguments. In general, the format is
```
python3 run_analysis.py <year> <process> --hists <output_filename>.root
```
For example, 
```
python3 run_analysis.py 2018 DYJets --hists DYJets.root
```
The options for background processes are `DYJets`, `tt+tW`, `tt_semileptonic`, `WJets`, `Diboson`, `Triboson`, `ttX`, `SingleTop`.

There are two additional optional arguments:

`--executor lpc`: Specify whether or not to run on the LPC. If this argument is used, one must first start an apptainer shell with a coffea environment by running `./shell coffeateam/coffea-dask-almalinux8:latest`.

`--masses`: Generate a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$).

Lastly, for debugging purposes one can also change the `max_chunks` and `max_files` parameters inside the `run_analysis.py` script to significantly shorten the analysis time. The `--hists` argument can also be omitted if no histograms are desired.

The output root file of histograms is stored in the `root_outputs/hists` directory.

## Plotting
### Merge root files
Once all of the MC processes have been analyzed, there will be a seperate root file for each of them. Before plotting, these should be merged into one file. First, go to the directory where the histograms are saved,
```
cd root_outputs/hists
```
Make a new directory, and move all of the root files there. For example
```
mkdir 2018ULbkg
mv *.root 2018ULbkg/
```
Go back to the `WrCoffea` directory and run the following command to merge the histograms,
```
python3 merge_hists.py <input_dir> <output_file>
```
For example,
```
python3 merge_hists.py root_outputs/hists/2018ULbkg 2018ULbkg.root
```
This will produce a single backgrounds file, `2018ULbkg.root`, with folders corresponding to the different files that were produced during the previous step.

### Plotting

To plot histograms, run
```
python3 plotting/plot_histograms.py
```
This will make plots of all of the histograms in the combined background root file. Bin sizes, x- and y-axis labels and limits for each histogram are all uniquely specified in the file
```
plotting/histogram_configs.py 
```

### Running on data
```
./shell coffeateam/coffea-dask-almalinux8:latest
```
To run over all 2018 data, enter the command 
```
python3 run_analysis.py 2018 Data --hists Data.root --executor lpc
```
The shell should then show
```
Starting an LPC Cluster

Starting to analyze 2018 Data files
Analyzing 241608232 SingleMuon Run2018A events.
Analyzing 119918017 SingleMuon Run2018B events.
Analyzing 109986009 SingleMuon Run2018C events.
Analyzing 513909894 SingleMuon Run2018D events.
Analyzing 339013231 EGamma Run2018A events.
Analyzing 153792795 EGamma Run2018B events.
Analyzing 147827904 EGamma Run2018C events.
Analyzing 752524583 EGamma Run2018D events.

Computing histograms...
```
The output is a root file (`Data.root`) containing histograms of kinematic variables across all basic analysis regions.

### Running on MC
The command below will locally analyze one root file from the 2018 UL DY+Jets background MC sample:
```
python3 run_analysis.py 2018 DYJets --hists example_hists.root --max_files 1
```

### Arguments
To run the analyzer, a sample set and process must be specified as arguments:

#### Mandatory Arguments
 - Year: Currently, only `2018` exists, but there are also plans to include the rest of Run II (2016 and 2017).
 - Process: The process to be analyzed. Options for background processes are `DYJets`, `tt+tW`, `tt_semileptonic`, `WJets`, `Diboson`, `Triboson`, `ttX`, `SingleTop`. To analyze signal MC samples, use `Signal`, or `Data` for Data.
 - Signal Mass: If the process is `Signal`, then the signal masses must also be specified via the flag `--mass`, for example `--mass MWR3000_MN2900`. To see all possible signal points, use `--help`.

#### Optional Arguments

`--hists`: Generate a root file with histograms of kinematic observables.

`--masses`: Generate a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$) (only implemented if the process is `Signal`).

`--max_files`: Generate a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$) (only implemented if the process is `Signal`).

`--executor`: Specify whether or not to run on the LPC. To run on the LPC, one must also run `./shell coffeateam/coffea-dask-almalinux8:latest`.

To run the analyzer without computing any output files (perhaps for debugging purposes), omit both `--hists` and `--masses`.

For more information, enter:
```
python3 run_analysis.py --help
```
