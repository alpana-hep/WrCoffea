from coffea import processor
from coffea.analysis_tools import Weights, PackedSelection
import awkward as ak
import hist.dask as dah
import hist
import numpy as np
import time
import logging
import warnings
warnings.filterwarnings("ignore",module="coffea.*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point=None):
        self._signal_sample = mass_point

        self.make_output = lambda: {
            'Jet_0_Pt': self.create_hist('pt_leadjet', 'process', 'region', (200, 0, 2000), r'p_{T} of the leading jet [GeV]'),
            'Jet_1_Pt': self.create_hist('pt_subleadjet', 'process', 'region', (200, 0, 2000), r'p_{T} of the subleading jet [GeV]'),
            'Lepton_0_Eta': self.create_hist('eta_leadlep', 'process', 'region', (60, -3, 3), r'#eta of the leading lepton'),
            'Lepton_0_Pt': self.create_hist('pt_leadlep', 'process', 'region', (200, 0, 2000), r'p_{T} of the leading lepton [GeV]'),
            'Lepton_1_Eta': self.create_hist('eta_subleadlep', 'process', 'region', (60, -3, 3), r'#eta of the subleading lepton'),
            'Lepton_1_Pt': self.create_hist('pt_subleadlep', 'process', 'region', (200, 0, 2000), r'p_{T} of the subleading lepton [GeV]'),
            'NCand_Lepton_0_Mass': self.create_hist('mass_threeobject_leadlep', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),
            'NCand_Lepton_0_Pt': self.create_hist('pt_threeobject_leadlep', 'process', 'region', (800, 0, 8000), r'p^{T}_{ljj} [GeV]'),
            'NCand_Lepton_1_Mass': self.create_hist('mass_threeobject_subleadlep', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),
            'NCand_Lepton_1_Pt': self.create_hist('pt_threeobject_subleadlep', 'process', 'region', (800, 0, 8000), r'p^{T}_{ljj} [GeV]'),
            'WRCand_Mass': self.create_hist('mass_fourobject', 'process', 'region', (800, 0, 8000), r'm_{lljj} [GeV]'),
            'WRCand_Pt': self.create_hist('pt_fourobject', 'process', 'region', (800, 0, 8000), r'p^{T}_{lljj} [GeV]'),
            'ZCand_Mass': self.create_hist('mass_dileptons', 'process', 'region', (5000, 0, 5000), r'm_{ll} [GeV]'),
            'ZCand_Pt': self.create_hist('pt_dileptons', 'process', 'region', (200, 0, 2000), r'p^{T}_{ll} [GeV]'),
            'ZCand_WRCand_Mass': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(800, 0, 8000, name='mass_dileptons', label=r'm_{ll} [GeV]'),
                hist.axis.Regular(800, 0, 8000, name='mass_fourobject', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
        }

    def create_hist(self, name, process, region, bins, label):
        """Helper function to create histograms."""
        return dah.hist.Hist(
            hist.axis.StrCategory([], name="process", label="Process", growth=True),
            hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
            hist.axis.Regular(*bins, name=name, label=label),
            hist.storage.Weight(),
        )

    def selectElectrons(self, events):
        """Select tight and loose electrons."""
        tight_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.cutBased_HEEP)
        loose_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.cutBased == 2)
        return events.Electron[tight_electrons], events.Electron[loose_electrons]

    def selectMuons(self, events):
        """Select tight and loose muons."""
        tight_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2) & (events.Muon.tkRelIso < 0.1)
        loose_muons= (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2)
        return events.Muon[tight_muons], events.Muon[loose_muons]

    def selectJets(self, events):
        """Select AK4 and AK8 jets."""
        ak4_jets = (events.Jet.pt > 40) & (np.abs(events.Jet.eta) < 2.4) & (events.Jet.isTightLeptonVeto)
        ak8_jets = (events.FatJet.pt > 200) & (np.abs(events.FatJet.eta) < 2.4) & (events.FatJet.jetId == 2) & (events.FatJet.msoftdrop > 40)
        return events.Jet[ak4_jets], events.FatJet[ak8_jets]

    def add_resolved_selections(self, selections, tightElectrons, tightMuons, AK4Jets, mlljj, dr_jl_min, dr_j1j2, dr_l1l2):
        selections.add("twoTightLeptons", (ak.num(tightElectrons) + ak.num(tightMuons)) == 2)
        selections.add("minTwoAK4Jets", ak.num(AK4Jets) >= 2)
        selections.add("leadTightLeptonPt60", (ak.any(tightElectrons.pt > 60, axis=1) | ak.any(tightMuons.pt > 60, axis=1)))
        selections.add("mlljj>800", mlljj > 800)
        selections.add("dr>0.4", (dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

    def fill_histograms(self, output, selections, region, cuts,  process, jets, leptons, weights):
        """Helper function to fill histograms dynamically."""
        # Define a list of variables and their corresponding histograms
        variables = [
            ('Jet_0_Pt', jets[:, 0].pt, 'pt_leadjet'),
            ('Jet_1_Pt', jets[:, 1].pt, 'pt_subleadjet'),
            ('Lepton_0_Eta', leptons[:, 0].eta, 'eta_leadlep'),
            ('Lepton_0_Pt', leptons[:, 0].pt, 'pt_leadlep'),
            ('Lepton_1_Eta', leptons[:, 1].eta, 'eta_subleadlep'),
            ('Lepton_1_Pt', leptons[:, 1].pt, 'pt_subleadlep'),
            ('NCand_Lepton_0_Mass', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_leadlep'),
            ('NCand_Lepton_0_Pt', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).pt, 'pt_threeobject_leadlep'),
            ('NCand_Lepton_1_Mass', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_subleadlep'),
            ('NCand_Lepton_1_Pt', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).pt, 'pt_threeobject_subleadlep'),
            ('WRCand_Mass', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_fourobject'),
            ('WRCand_Pt', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).pt, 'pt_fourobject'),
            ('ZCand_Mass', (leptons[:, 0] + leptons[:, 1]).mass, 'mass_dileptons'),
            ('ZCand_Pt', (leptons[:, 0] + leptons[:, 1]).pt, 'pt_dileptons'),
        ]

        # Apply the selections
        cut = selections.all(*cuts)

        # Loop over variables and fill corresponding histograms
        for hist_name, values, axis_name in variables:
            output[hist_name].fill(
                process=process,
                region=region,
                **{axis_name: values[cut]},
                weight=weights.weight()[cut]
            )

    def process(self, events): 
        output = self.make_output()
        
        metadata = events.metadata
        mc_campaign = metadata["mc_campaign"]
        process = metadata["process"]
        dataset = metadata["dataset"]
        isRealData = not hasattr(events, "genWeight")

        output['mc_campaign'] = mc_campaign
        output['process'] = process
        output['dataset'] = dataset
        if not isRealData:
            output['x_sec'] = events.metadata["xsec"] 

        logger.info(f"Analyzing {len(events)} {dataset} events.")
    
        # Object selection
        tightElectrons, _  = self.selectElectrons(events)
        nTightElectrons = ak.num(tightElectrons)

        tightMuons, _ = self.selectMuons(events)
        nTightMuons = ak.num(tightMuons)

        AK4Jets, _ = self.selectJets(events)
        nAK4Jets = ak.num(AK4Jets)

        # Weights
        weights = Weights(size=None, storeIndividual=True)
        eventWeight = events.genWeight
        weights.add("event_weight", weight=eventWeight)
        output['sumw'] = events.metadata["genEventSumw"]

        # Event variables
        tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons = ak.pad_none(tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)], 2, axis=1)
        AK4Jets = ak.pad_none(AK4Jets, 2, axis=1)

        mll = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1]).mass, False)
        mlljj = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1] + AK4Jets[:, 0] + AK4Jets[:, 1]).mass, False)

        dr_jl_min = ak.fill_none(ak.min(AK4Jets[:,:2].nearest(tightLeptons).delta_r(AK4Jets[:,:2]), axis=1), False)
        dr_j1j2 = ak.fill_none(AK4Jets[:,0].delta_r(AK4Jets[:,1]), False)
        dr_l1l2 = ak.fill_none(tightLeptons[:,0].delta_r(tightLeptons[:,1]), False)

        # Event selections
        selections = PackedSelection()
        self.add_resolved_selections(selections, tightElectrons, tightMuons, AK4Jets, mlljj, dr_jl_min, dr_j1j2, dr_l1l2)

        # Trigger selections
        eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
        muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100

        selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
        selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
        selections.add("emuTrigger", (eTrig & muTrig & (nTightElectrons == 1) & (nTightMuons == 1)))

        # Channel selections
        selections.add("eejj", ((nTightElectrons == 2) & (nTightMuons == 0)))
        selections.add("mumujj", ((nTightElectrons == 0) & (nTightMuons == 2)))
        selections.add("emujj", ((nTightElectrons == 1) & (nTightMuons == 1)))

        # mll selections
        selections.add("60mll150", ((mll > 60) & (mll < 150)))
        selections.add("150mll400", ((mll > 150) & (mll < 400)))
        selections.add("400mll", (mll > 400))
        selections.add("150mll", (mll > 150))

        # Define analysis regions
        regions = {
            'WR_EE_Resolved_DYCR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
            'WR_MuMu_Resolved_DYCR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
            'WR_EE_Resolved_DYSR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'WR_MuMu_Resolved_DYSR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],
            'WR_EMu_Resolved_Sideband': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
            'WR_EE_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'eejj'],
            'WR_MuMu_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'mumujj'],
            'WR_EMu_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'emujj'],
        }

        # Fill histograms
        for region, cuts in regions.items():
            self.fill_histograms(output, selections, region, cuts, process, AK4Jets, tightLeptons, weights)

        output["weightStats"] = weights.weightStatistics
        return output

    def postprocess(self, accumulator):
        return accumulator
