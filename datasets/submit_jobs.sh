#!/bin/bash

# Loop from 22 to 92, with a step of 2
for ((i=42; i<=74; i+=2))
do
  # Construct and run the python command
  python3 data_skim.py EGamma 2018 RunB --start $i
done
