# WrCoffea

## Coffea Introduction
To install coffea:
```
python3 -m pip install coffea --user
```
All coffea documentation is hosted at https://coffeateam.github.io/coffea/
## Getting Started
Begin by cloning the repository,
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
## Running the analyzer
### Example
The command below will locally analyze one root file from each of the 2018 UL background MC samples:
```
python3 run_analysis.py UL18_bkg allMC --hists example_hists.root --masses example_masses.root  --max_files 1
```
Two files are outputted: a root file containing histograms of kinematic variables across all basic analysis regions (`example_hists.root`), and a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$) (`example_masses.root`).

### Arguments
To run the analyzer, a sample set and process must be specified as arguments:

 - Sample sets: Currently, only `UL18_bkg` has been created, but there are also plans to include `UL18_signal` and `UL18_data` sample sets, as well as the rest of Run II (2016 and 2017).
 - Process: The MC process to be analyzed. Options for individual processes are `DYJets`, `tt+tW`, `WJets`, `Diboson`, `Triboson`, `ttX`, `SingleTop`, or to analyze the entire sample set, use `allMC`.

To analyze over all files for the given process, simply omit the `--max_files` flag. To run the analyzer without computing any output files (perhaps for debugging purposes), omit both `--output_hists` and `--output_masses`.

For more information, enter:
```
python3 run_analysis.py --help
```

## Future Work
In the near future there are plans to scale out the framework to use distributed computing resources needed to analyze all 2018 UL MC samples and files.
