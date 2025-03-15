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
xrdcp -r TbarWplusto2L2Nu_TuneCP5_13p6TeV_powheg-pythia8 root://cmseos.fnal.gov//store/user/wijackso/WRAnalyzer/skims/2025/Run3/2022/Run3Summer22
```
Repeat this process for each dataset. To view the EOS storage system, use
```
eosls -lh store/user/wijackso/WRAnalyzer/skims/2025/Run3/2022/Run3Summer22
```
