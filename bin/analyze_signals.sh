#!/bin/bash

python3 test/run_analysis_mll.py Run2Autumn18 Signal --mass MWR2000_MN600 --hists

python3 test/run_analysis_mll.py Run2Autumn18 Signal --mass MWR2000_MN1000 --hists

python3 test/run_analysis_mll.py Run2Autumn18 Signal --mass MWR2000_MN1400 --hists

python3 test/run_analysis_mll.py Run2Autumn18 Signal --mass MWR2000_MN1800 --hists
