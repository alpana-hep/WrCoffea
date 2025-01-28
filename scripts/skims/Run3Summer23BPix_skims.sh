#!/bin/bash

#for ((i=1; i<=197; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-40to70 --start $i
#done

#for ((i=1; i<=245; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-70to100 --start $i
#done

#for ((i=1; i<=294; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-100to400 --start $i
#done

#for ((i=1; i<=22; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-400to800 --start $i
#done

#for ((i=1; i<=43; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-800to1500 --start $i
#done

#for ((i=1; i<=63; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-1500to2500 --start $i
#done

#for ((i=1; i<=57; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-50to120_HT-2500 --start $i
#done

for ((i=1; i<=16; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-40to70 --start $i
done

for ((i=1; i<=42; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-70to100 --start $i
done

for ((i=1; i<=30; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-100to400 --start $i
done

for ((i=1; i<=67; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-400to800 --start $i
done

for ((i=1; i<=71; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-800to1500 --start $i
done

for ((i=1; i<=84; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-1500to2500 --start $i
done

for ((i=1; i<=38; i+=1))
do
    python3 skim_files.py Run3Summer23BPix DYto2L-4Jets_MLL-120_HT-2500 --start $i
done

#for ((i=1; i<=150; i+=1))
#do
#    python3 skim_files.py Run3Summer23BPix TTto2L2Nu --start $i
#done
