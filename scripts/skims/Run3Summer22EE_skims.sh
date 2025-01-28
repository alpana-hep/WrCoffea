#!/bin/bash

for ((i=1; i<=422; i+=1))
do
    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-40to70 --start $i
done

for ((i=1; i<=648; i+=1))
do
    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-70to100 --start $i
done

for ((i=1; i<=307; i+=1))
do
    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-100to400 --start $i
done

#for ((i=1; i<=52; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-400to800 --start $i
#done

#for ((i=1; i<=129; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-800to1500 --start $i
#done

#for ((i=1; i<=170; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-1500to2500 --start $i
#done

#for ((i=1; i<=154; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-50to120_HT-2500 --start $i
#done

#for ((i=1; i<=125; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-40to70 --start $i
#done

#for ((i=1; i<=107; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-70to100 --start $i
#done

#for ((i=1; i<=77; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-100to400 --start $i
#done

#for ((i=1; i<=122; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-400to800 --start $i
#done

#for ((i=1; i<=132; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-800to1500 --start $i
#done

#for ((i=1; i<=135; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-1500to2500 --start $i
#done

#for ((i=1; i<=116; i+=1))
#do
#    python3 skim_files.py DYto2L-4Jets_MLL-120_HT-2500 --start $i
#done

#for ((i=1; i<=137; i+=1))
#do
#    python3 skim_files.py TTto2L2Nu --start $i
#done
