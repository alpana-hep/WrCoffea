## Cross-section Computation
### Find MINIAOD files
* Create a `.txt` file with MINIAOD DAS dataset names in the directory `data/miniaod`.
* Execute the script `miniaod_files.py`. This takes in these dataset names, quieries DAS, and makes `.txt` files containing individual file paths for each dataset.
```
cd scripts/setup
python3 miniaod_files.py Run3Summer23BPix
```

### Compute the cross-section
* To compute the cross section go a `cmssw` environment,
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

* Save the above output to a `.log` file in `data/x-secs/`.
