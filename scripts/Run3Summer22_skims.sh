#!/bin/bash

for ((i=1; i<=79; i+=1))
do
    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-40to70 --start $i
done

#for ((i=1; i<=72; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-70to100 --start $i
#done

#for ((i=1; i<=127; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-100to400 --start $i
#done

#for ((i=1; i<=23; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-400to800 --start $i
#done

#for ((i=1; i<=52; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-800to1500 --start $i
#done

#for ((i=1; i<=68; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-1500to2500 --start $i
#done

#for ((i=1; i<=52; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-2500 --start $i
#done

#for ((i=1; i<=19; i+=1))
#do
#    python3 skim_files.py DYJetsToLL_M-50_HT-2500toInf --start $i
#done

#for ((i=6; i<=155; i+=1))
#do
#    python3 skim_files.py TTTo2L2Nu --start $i
#done

#for ((i=1; i<=16; i+=1))
#do
#    python3 skim_files.py ST_tW_antitop --start $i
#done

#for ((i=1; i<=15; i+=1))
#do
#    python3 skim_files.py ST_tW_top --start $i
#done

#for ((i=1; i<=97; i+=1))
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

for ((i=341; i<=355; i+=1))
do
  # Construct and run the python command
  python3 skim_files.py EGamma_Run2018D --start $i
done
