# WrCoffea

## Getting Started
Begin by cloning the repository:
```
git clone git@github.com:UMN-CMS/WrCoffea.git
cd WrCoffea
```
## Running the analyzer
To run the analyzer:
```
python3 analyzer.py
```
This will process a nanoAOD file of $t\bar{t}$ events and output a root file containing histograms.
## Framework
The analyzer and framework are loosely based on the following analysis:

https://github.com/iris-hep/analysis-grand-challenge/tree/main/analyses/cms-open-data-ttbar

In particular, see `ttbar_analysis_pipeline.py`.
