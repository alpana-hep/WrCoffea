#!/usr/bin/env python3

import numpy as np
import awkward as ak

#nums_list = [[2,4], [9,1], [3,6], [1,7], [2,5]]

#awkward_nums_list = ak.Array(nums_list)

#print(awkward_nums_list)

#print(np.sqrt(awkward_nums_list))

elec_fields = ['deltaEtaSC', 'dr03EcalRecHitSumEt', 'dr03HcalDepth1TowerSumEt', 'dr03TkSumPt', 'dr03TkSumPtHEEP', 'dxy', 'dxyErr', 'dz', 'dzErr', 'eCorr', 'eInvMinusPInv', 'energyErr', 'eta', 'hoe', 'ip3d', 'jetPtRelv2', 'jetRelIso', 'mass', 'miniPFRelIso_all', 'miniPFRelIso_chg', 'mvaFall17V1Iso', 'mvaFall17V1noIso', 'mvaFall17V2Iso', 'mvaFall17V2noIso', 'pfRelIso03_all', 'pfRelIso03_chg', 'phi', 'pt', 'r9', 'scEtOverPt', 'sieie', 'sip3d', 'mvaTTH', 'charge', 'cutBased', 'cutBased_Fall17_V1', 'jetIdx', 'pdgId', 'photonIdx', 'tightCharge', 'vidNestedWPBitmap', 'vidNestedWPBitmapHEEP', 'convVeto', 'cutBased_HEEP', 'isPFcand', 'lostHits', 'mvaFall17V1Iso_WP80', 'mvaFall17V1Iso_WP90', 'mvaFall17V1Iso_WPL', 'mvaFall17V1noIso_WP80', 'mvaFall17V1noIso_WP90', 'mvaFall17V1noIso_WPL', 'mvaFall17V2Iso_WP80', 'mvaFall17V2Iso_WP90', 'mvaFall17V2Iso_WPL', 'mvaFall17V2noIso_WP80', 'mvaFall17V2noIso_WP90', 'mvaFall17V2noIso_WPL', 'seedGain', 'genPartIdx', 'genPartFlav', 'cleanmask', 'genPartIdxG', 'jetIdxG', 'photonIdxG']

muon_fields = ['dxy', 'dxyErr', 'dxybs', 'dz', 'dzErr', 'eta', 'ip3d', 'jetPtRelv2', 'jetRelIso', 'mass', 'miniPFRelIso_all', 'miniPFRelIso_chg', 'pfRelIso03_all', 'pfRelIso03_chg', 'pfRelIso04_all', 'phi', 'pt', 'ptErr', 'segmentComp', 'sip3d', 'softMva', 'tkRelIso', 'tunepRelPt', 'mvaLowPt', 'mvaTTH', 'charge', 'jetIdx', 'nStations', 'nTrackerLayers', 'pdgId', 'tightCharge', 'fsrPhotonIdx', 'highPtId', 'highPurity', 'inTimeMuon', 'isGlobal', 'isPFcand', 'isTracker', 'looseId', 'mediumId', 'mediumPromptId', 'miniIsoId', 'multiIsoId', 'mvaId', 'pfIsoId', 'softId', 'softMvaId', 'tightId', 'tkIsoId', 'triggerIdLoose', 'genPartIdx', 'genPartFlav', 'cleanmask', 'fsrPhotonIdxG', 'genPartIdxG', 'jetIdxG']

lepton_fields = []

for field in elec_fields:
    if field in muon_fields:
        lepton_fields.append(field)

#print("lepton_fields --> " + str(lepton_fields))

new_fields = ['dxy', 'dxyErr', 'dz', 'dzErr', 'eta', 'ip3d', 'jetPtRelv2', 'jetRelIso', 'mass', 'miniPFRelIso_all', 'miniPFRelIso_chg', 'pfRelIso03_all', 'pfRelIso03_chg', 'phi', 'pt', 'sip3d', 'mvaTTH', 'charge', 'jetIdx', 'pdgId', 'tightCharge', 'isPFcand', 'genPartIdx', 'genPartFlav', 'cleanmask', 'genPartIdxG', 'jetIdxG']

if new_fields == elec_fields:
    print("electron fields")
if new_fields == muon_fields:
    print("muon fields")
if new_fields == lepton_fields:
    print("lepton fields")

for field in elec_fields:
    if field == 'px':
        print('px found in elec_fields')
for field in muon_fields:
    if field == 'px':
        print('px found in muon_fields')
