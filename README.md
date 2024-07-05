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
The command below will locally analyze one root file from the 2018 UL DY+Jets background MC sample:
```
python3 run_analysis.py 2018 DYJets --hists example_hists.root --max_files 1
```
The output is a root file (`example_hists.root`) containing histograms of kinematic variables across all basic analysis regions, and a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$) (`example_masses.root`).

### Arguments
To run the analyzer, a sample set and process must be specified as arguments:

#### Mandatory Arguments
 - Year: Currently, only `2018` exists, but there are also plans to include the rest of Run II (2016 and 2017).
 - Process: The process to be analyzed. Options for background processes are `DYJets`, `tt+tW`, `tt_semileptonic`, `WJets`, `Diboson`, `Triboson`, `ttX`, `SingleTop`, or to analyze signal MC samples, use `Signal`.
 - Signal Mass: If the process is `Signal`, then the signal masses must also be specified via the flag `--mass`, for example `--mass MWR3000_MN2900`. To see all possible signal points, use `--help`.

#### Optional Arguments

`--hists`: Generate a root file with histograms of kinematic observables.
`--masses`: Generate a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$) (only implemented if the process is `Signal`).
`--max_files`: Generate a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$) (only implemented if the process is `Signal`).

To run the analyzer without computing any output files (perhaps for debugging purposes), omit both `--hists` and `--masses`.

For more information, enter:
```
python3 run_analysis.py --help
```
