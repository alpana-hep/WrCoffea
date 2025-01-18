#!/bin/bash

for ((i=1; i<=13; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-70to100 --start $i
done

for ((i=1; i<=30; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-100to200 --start $i
done

for ((i=1; i<=21; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-200to400 --start $i
done

for ((i=1; i<=28; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-400to600 --start $i
done

for ((i=1; i<=11; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-600to800 --start $i
done

for ((i=1; i<=24; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-800to1200 --start $i
done

for ((i=1; i<=13; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-1200to2500 --start $i
done

for ((i=1; i<=19; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-2500toInf --start $i
done

#for ((i=1; i<=155; i+=1))
#do
#    python3 skim_files.py TTTo2L2Nu --start $i
#done

#for ((i=13; i<=16; i+=1))
#do
#    python3 skim_files.py ST_tW_antitop --start $i
#done

#for ((i=1; i<=15; i+=1))
#do
#    python3 skim_files.py ST_tW_top --start $i
#done

#for ((i=37; i<=97; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-70To100 --start $i
#done

#for ((i=1; i<=57; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-100To200 --start $i
#done

#for ((i=1; i<=101; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-200To400 --start $i
#done

#for ((i=1; i<=44; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-400To600 --start $i
#done

#for ((i=1; i<=33; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-600To800 --start $i
#done

#for ((i=1; i<=11; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-800To1200 --start $i
#done

#for ((i=1; i<=8; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-1200To2500 --start $i
#done

#for ((i=1; i<=51; i+=1))
#do
#    python3 skim_files.py WJetsToLNu_HT-2500ToInf --start $i
#done

#for ((i=1; i<=31; i+=1))
#do
#    python3 skim_files.py WW --start $i
#done

#for ((i=1; i<=16; i+=1))
#do
#    python3 skim_files.py WZ --start $i
#done

#for ((i=1; i<=6; i+=1))
#do
#    python3 skim_files.py ZZ --start $i
#done

#for ((i=1; i<=5; i+=1))
#do
#    python3 skim_files.py WWW --start $i
#done

#for ((i=1; i<=5; i+=1))
#do
#    python3 skim_files.py WWZ --start $i
#done

#for ((i=1; i<=15; i+=1))
#do
#    python3 skim_files.py WZZ --start $i
#done

#for ((i=1; i<=14; i+=1))
#do
#    python3 skim_files.py ZZZ --start $i
#done

#for ((i=30; i<=42; i+=1))
#do
#    python3 skim_files.py ttWJets --start $i
#done

#for ((i=1; i<=52; i+=1))
#do
#    python3 skim_files.py ttZJets --start $i
#done

#for ((i=1; i<=19; i+=1))
#do
#    python3 skim_files.py ST_s-channel --start $i
#done

#for ((i=60; i<=132; i+=1))
#do
#    python3 skim_files.py ST_t-channel_antitop --start $i
#done

#for ((i=1; i<=196; i+=1))
#do
#    python3 skim_files.py ST_t-channel_top --start $i
#done

#for ((i=1; i<=391; i+=1))
#do
#    python3 skim_files.py TTToSemiLeptonic --start $i
#done

#for ((i=1; i<=226; i+=1))
#do
  # Construct and run the python command
#  python3 skim_files.py EGamma_Run2018A --start $i
#done

#for ((i=44; i<=74; i+=1))
#do
  # Construct and run the python command
#  python3 skim_files.py EGamma_Run2018B --start $i
#done

#for ((i=1; i<=83; i+=1))
#do
  # Construct and run the python command
#  python3 skim_files.py EGamma_Run2018B --start $i
#done

#for ((i=1; i<=355; i+=1))
#do
  # Construct and run the python command
#  python3 skim_files.py EGamma_Run2018D --start $i
#done


