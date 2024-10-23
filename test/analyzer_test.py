from coffea import processor
import warnings
from coffea.analysis_tools import Weights
warnings.filterwarnings("ignore",module="coffea.*")
import numpy as np
import awkward as ak
import hist.dask as dah
import hist
import dask.array as da
import dask_awkward as dak
from coffea.analysis_tools import PackedSelection
import time

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point=None):
        self._signal_sample = mass_point
        self.make_output = lambda: {
            'pt_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(200, 0, 500, name='pt_leadlep', label=r'p_{T} of the leading lepton [GeV]', overflow=True),
                hist.storage.Weight(),
            ),
            'pt_leadjet': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(200, 0, 2000, name='pt_leadjet', label=r'p_{T} of the leading jet [GeV]'),
                hist.storage.Weight(),
            ),
            'mass_dileptons': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(800, 0, 8000, name='mass_dileptons', label=r'm_{ll} [GeV]'),
                hist.storage.Weight(),
            ),
            'mass_fourobject': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(800, 0, 8000, name='mass_fourobject', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
        }

    def process(self, events): 
        output = self.make_output()

        isRealData = not hasattr(events, "genWeight")

        output['mc_campaign'] = events.metadata["mc_campaign"]

        if not isRealData:
            output['x_sec'] = events.metadata["xsec"]

        process = events.metadata["process"]
        output['process'] = process

        dataset = events.metadata["dataset"]
        output['dataset'] = dataset

        isMC = hasattr(events, "genWeight")

        print(f"Analyzing {len(events)} {dataset} events.")

        ####################
        # OBJECT SELECTION #
        ####################

        tightElectrons, looseElectrons = selectElectrons(events)
        nTightElectrons = ak.num(tightElectrons)

        tightMuons, looseMuons = selectMuons(events)
        nTightMuons = ak.num(tightMuons)

        AK4Jets, AK8Jets = selectJets(events)
        nAK4Jets = ak.num(AK4Jets)

        ###########
        # WEIGHTS #
        ###########

        weights = Weights(size=None, storeIndividual=True)
        if not isRealData:
            eventWeight = events.genWeight #or eventWeight = np.sign(events.genWeight)
        else:
            eventWeight = abs(np.sign(events.event))

        #Only fill histogram with event specific weights
        weights.add("event_weight", weight=eventWeight)

        if not isRealData:
            output['sumw'] = ak.sum(eventWeight) # or output['sumw'] = events.metadata["genEventSumw"]

        ###################
        # EVENT VARIABLES #
        ###################

        tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons = ak.pad_none(tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)], 2, axis=1)
        AK4Jets = ak.pad_none(AK4Jets, 2, axis=1)

        mll = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1]).mass, False)
        mlljj = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1] + AK4Jets[:, 0] + AK4Jets[:, 1]).mass, False)

        dr_jl_min = ak.fill_none(ak.min(AK4Jets[:,:2].nearest(tightLeptons).delta_r(AK4Jets[:,:2]), axis=1), False)
        dr_j1j2 = ak.fill_none(AK4Jets[:,0].delta_r(AK4Jets[:,1]), False)
        dr_l1l2 = ak.fill_none(tightLeptons[:,0].delta_r(tightLeptons[:,1]), False)


        ###################
        # EVENT SELECTION #
        ###################

        selections = PackedSelection()

        # Resolved Selections
        selections.add("twoTightLeptons", (nTightElectrons + nTightMuons) == 2)
        selections.add("minTwoAK4Jets", (nAK4Jets >= 2))
        selections.add("leadTightLeptonPt60", ((ak.any(tightElectrons.pt > 60, axis=1)) | (ak.any(tightMuons.pt > 60, axis=1))))
        selections.add("mlljj>800", (mlljj > 800))
        selections.add("dr>0.4", (dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

        # Trigger Selections

        if not isRealData:
            eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
            muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100
#            muTrig = events.HLT.Mu50
            selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
            selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
            selections.add("emuTrigger", (eTrig & muTrig & (nTightElectrons == 1) & (nTightMuons == 1)))

        # Flavor Selections
        selections.add("eejj", ((nTightElectrons == 2) & (nTightMuons == 0)))
        selections.add("mumujj", ((nTightElectrons == 0) & (nTightMuons == 2)))
        selections.add("emujj", ((nTightElectrons == 1) & (nTightMuons == 1)))

        # mll Selections
        selections.add("60mll150", ((mll > 60) & (mll < 150)))
        selections.add("150mll400", ((mll > 150) & (mll < 400)))
        selections.add("400mll", (mll > 400))
        selections.add("150mll", (mll > 150))

        regions = {
            'eejj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
            'mumujj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
            'emujj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'emujj'],
            'eejj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'eejj'],
            'mumujj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'mumujj'],
            'emujj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'emujj'],
            'eejj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'mumujj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],
            'emujj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
            'eejj_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'eejj'],
            'mumujj_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'mumujj'],
            'emujj_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'emujj'],
        }

        ###################
        # FILL HISTOGRAMS #
        ###################

        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            output['pt_leadlep'].fill(process=process, region=region, pt_leadlep=tightLeptons[cut][:, 0].pt, weight=weights.weight()[cut])
            output['pt_leadjet'].fill(process=process, region=region, pt_leadjet=AK4Jets[cut][:, 0].pt, weight=weights.weight()[cut])
            output['mass_dileptons'].fill(process=process, region=region, mass_dileptons=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).mass, weight=weights.weight()[cut])
            output['mass_fourobject'].fill(process=process, region=region, mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass, weight=weights.weight()[cut])

        output["weightStats"] = weights.weightStatistics
        print("sumw", output["weightStats"]["event_weight"]["sumw"].compute())
        print("minw", output["weightStats"]["event_weight"]["minw"].compute())
        print("maxw", output["weightStats"]["event_weight"]["maxw"].compute())
        print("sumw", output['sumw'].compute())
        return output

    def postprocess(self, accumulator):
        return accumulator

def selectElectrons(events):
    # select tight electrons
    electronSelectTight = (
            (events.Electron.pt > 53)
            & (np.abs(events.Electron.eta) < 2.4)
            & (events.Electron.cutBased_HEEP)
    )

    # select loose electrons
    electronSelectLoose = (
            (events.Electron.pt > 53)
            & (np.abs(events.Electron.eta) < 2.4)
            & (events.Electron.cutBased == 2)

    )
    return events.Electron[electronSelectTight], events.Electron[electronSelectLoose]

def selectMuons(events):
    # select tight muons
    muonSelectTight = (
            (events.Muon.pt > 53)
            & (np.abs(events.Muon.eta) < 2.4)
            & (events.Muon.highPtId == 2)
            & (events.Muon.tkRelIso < 0.1)
    )

    # select loose muons
    muonSelectLoose = (
            (events.Muon.pt > 53) 
            & (np.abs(events.Muon.eta) < 2.4) 
            & (events.Muon.highPtId == 2)
    )

    return events.Muon[muonSelectTight], events.Muon[muonSelectLoose] 

def selectJets(events):
    # select AK4 jets
#    hem_issue = ((-3.0 < events.Jet.eta < -1.3) & (-1.57 < events.Jet.phi < -0.87))

    jetSelectAK4 = (
            (events.Jet.pt > 40)
             & (np.abs(events.Jet.eta) < 2.4)
            & (events.Jet.isTightLeptonVeto)
    )

    # select AK8 jets (need to add LSF cut)
    jetSelectAK8 = (
            (events.FatJet.pt > 200)
            & (np.abs(events.FatJet.eta) < 2.4)
            & (events.FatJet.jetId == 2)
            & (events.FatJet.msoftdrop > 40)
    )

    return events.Jet[jetSelectAK4], events.FatJet[jetSelectAK8]
