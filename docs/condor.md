## Running on Condor on the LPC
From the working directory of your project, download and run the boostrap script:
```
curl -OL https://raw.githubusercontent.com/CoffeaTeam/lpcjobqueue/main/bootstrap.sh
bash bootstrap.sh
```
Note this only needs to be done once.

This creates two new files in this directory: `shell` and `.bashrc`. The `./shell` executable can then be used to start an apptainer shell with a coffea environment. The current image I use is
```
./shell coffeateam/coffea-base-almalinux9:0.7.29-py3.10
```
If you face issues with python mismatch then run the above command after unsetting python path shell variables
```
unset PYTHONHOME
unset PYTHONPATH
```

Then, run the analyzer with the `--condor` option,
```
python3 bin/run_analysis.py Run3Summer22EE DYJets --condor
```
