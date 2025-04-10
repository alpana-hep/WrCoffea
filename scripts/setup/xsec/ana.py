import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import sys
import io
import os

options = VarParsing ('analysis')
options.parseArguments()
process = cms.Process('XSec')

process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(options.maxEvents)
)

process.load('FWCore.MessageService.MessageLogger_cfi')
process.MessageLogger.cerr.FwkReport.reportEvery = 100000

secFiles = cms.untracked.vstring() 

# Read file names from an external text file
if len(options.inputFiles) == 1 and options.inputFiles[0].endswith('.txt'):
    with open(options.inputFiles[0], 'r') as f:
        fileNames = cms.untracked.vstring(f.read().splitlines())
else:
    fileNames = cms.untracked.vstring(options.inputFiles)

process.source = cms.Source ("PoolSource",
    fileNames = fileNames, 
    secondaryFileNames = secFiles)
process.xsec = cms.EDAnalyzer("GenXSecAnalyzer")

process.ana = cms.Path(process.xsec)
process.schedule = cms.Schedule(process.ana)
