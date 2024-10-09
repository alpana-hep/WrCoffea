#!/bin/bash

for ((i=10; i<=30; i+=1))
do
    python3 skim_files.py DYJetsToLL_M-50_HT-100to200 --start $i
done
