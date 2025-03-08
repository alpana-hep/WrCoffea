### Plotting
Plotting is handled in the `WR_Plotter` submodule,
```
cd WR_Plotter
```

Source the appropriate LGC release. For example,
```
source /cvmfs/sft.cern.ch/lcg/views/LCG_104/x86_64-centos8-gcc11-opt/setup.sh
```

To plot a comparison of the Run2 vs. Run3 backgrounds,
```
python3 scripts/241120_Run2VSRun3/plot_CR.py --umn
```

To plot a comparison of the signal masses,
```
python3 scripts/241215_N3000_vs_N800/plot_SR.py --umn
```
