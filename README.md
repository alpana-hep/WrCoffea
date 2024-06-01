# WrCoffea

## Coffea Introduction
To install coffea:
```
python3 -m pip install coffea --user
```
All coffea documentation is hosted at https://coffeateam.github.io/coffea/
## Getting Started
Begin by cloning the repository:
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
## Running the analyzer
### Example
The command below will locally analyze one DY nanoAOD root file and one $t\bar{t}$  file from the 2018 UL MC samples:
```
python3 run_analysis.py UL18_bkg --output_hists example_hists.root  --max_files 1
```
The output is a root file (`example_hists.root`) containing histograms of kinematic variables, across all basic analysis regions. 

### Arguments
To run the analyzer, a sample set must be given as an argument. Currently, only `UL18_bkg` has been created, but there are also plans to include `UL18_signal` and `UL18_data` sample sets, as well as the rest of Run II (2016 and 2017). 

There is an additional optional flag `--output_masses` that outputs a root file with branches of the 3-object invariant mass ($m_{ljj}$) and 4-object invariant mass ($m_{lljj}$). To analyze over all files in each dataset, simply omit the `--max_files` flag. To run the analyzer without computing any output files, omit both `--output_hists` and `--output_masses`.

In the near future there are plans to scale out the framework to use distributed computing resources needed to analyze all MC samples.

## Future Work
In the near future there are plans to scale out the framework to use distributed computing resources needed to analyze all 2018 UL MC samples and files.
