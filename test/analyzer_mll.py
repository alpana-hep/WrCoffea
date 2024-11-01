from coffea import processor
from coffea.analysis_tools import Weights, PackedSelection
import awkward as ak
import hist.dask as dah
import hist
import numpy as np
import re
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
            'event_weight': self.create_hist('event_weight', 'process', 'region', (1,0,1), r'Event count without cuts'),
            'NCand_Lepton_0_Mass': self.create_hist('mass_threeobject_leadlep', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),
            'NCand_Lepton_1_Mass': self.create_hist('mass_threeobject_subleadlep', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),
            'WRCand_Mass': self.create_hist('mass_fourobject', 'process', 'region', (800, 0, 8000), r'm_{lljj} [GeV]'),
            'ZCand_Mass': self.create_hist('mass_dileptons', 'process', 'region', (5000, 0, 5000), r'm_{ll} [GeV]'),
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

    def check_mass_point_resolved(self):
        """Check if the specified mass point is a resolved sample.

        Raises:
            NotImplementedError: If MN/MWR is less than 0.2, indicating an unresolved sample.
            ValueError: If the mass point format in _signal_sample is invalid.
        """
        match = re.match(r"MWR(\d+)_MN(\d+)", self._signal_sample)
        if match:
            mwr, mn = int(match.group(1)), int(match.group(2))
            ratio = mn / mwr
            if ratio < 0.2:
                raise NotImplementedError(
                    f"Choose a resolved sample (MN/MWR > 0.2). For this sample, MN/MWR = {ratio:.2f}."
                )
        else:
            raise ValueError(f"Invalid mass point format: {self._signal_sample}")

    def add_resolved_selections(self, selections, tightElectrons, tightMuons, AK4Jets, mlljj, dr_jl_min, dr_j1j2, dr_l1l2):
        selections.add("twoTightLeptons", (ak.num(tightElectrons) + ak.num(tightMuons)) == 2)
        selections.add("minTwoAK4Jets", ak.num(AK4Jets) >= 2)
        selections.add("leadTightLeptonPt60", (ak.any(tightElectrons.pt > 60, axis=1) | ak.any(tightMuons.pt > 60, axis=1)))
        selections.add("mlljj>800", mlljj > 800)
        selections.add("dr>0.4", (dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

    def fill_basic_histograms(self, output, region, cut,  process, jets, leptons, weights):
        """Helper function to fill histograms dynamically."""
        # Define a list of variables and their corresponding histograms
        variables = [
            ('NCand_Lepton_0_Mass', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_leadlep'),
            ('NCand_Lepton_1_Mass', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_subleadlep'),
            ('WRCand_Mass', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_fourobject'),
            ('ZCand_Mass', (leptons[:, 0] + leptons[:, 1]).mass, 'mass_dileptons'),

        ]

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
        isMC = hasattr(events, "genWeight")
        
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
        if isMC:
            # Apply triggers for MC
            if mc_campaign == "Run2Summer20UL18" or mc_campaign == "Run2Autumn18":
                eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
                muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100
                selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
                selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
                selections.add("emuTrigger", (eTrig & muTrig & (nTightElectrons == 1) & (nTightMuons == 1)))
            elif mc_campaign == "Run3Summer22":
                eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
                muTrig = events.HLT.Mu50 | events.HLT.HighPtTkMu100
                selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
                selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
                selections.add("emuTrigger", (eTrig & muTrig & (nTightElectrons == 1) & (nTightMuons == 1)))

            # Use genWeight for MC
            eventWeight = events.genWeight
            if process == "Signal":
                output['sumw'] = ak.sum(eventWeight)
            else:
                output['sumw'] = events.metadata["genEventSumw"]
        elif isRealData:
            # Fill the data weights with one
            eventWeight = abs(np.sign(events.event)) # Find a better way to do this

        # Weights
        weights = Weights(size=None, storeIndividual=True)
        weights.add("event_weight", weight=eventWeight)

        # Channel selections
        selections.add("eejj", ((nTightElectrons == 2) & (nTightMuons == 0)))
        selections.add("mumujj", ((nTightElectrons == 0) & (nTightMuons == 2)))
        selections.add("emujj", ((nTightElectrons == 1) & (nTightMuons == 1)))

        # mll selections
        selections.add("60mll150", ((mll > 60) & (mll < 150)))
        selections.add("400mll", (mll > 400))
        selections.add("150mll", (mll > 150))

        # Define analysis regions
        regions = {
            'WR_EE_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'eejj'],
            'WR_MuMu_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'mumujj'],
            'WR_EMu_150mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '150mll', 'emujj'],
        }

        # Blind signal region and remove triggers
        if isRealData:
            # Remove specific regions
            for region in ['WR_EE_150mll', 'WR_MuMu_150mll', 'WR_EMu_150mll']:
                regions.pop(region, None)  # Use pop with a default to avoid KeyError

            # Remove triggers from all remaining regions
            elements_to_remove = {'mumuTrigger', 'eeTrigger', 'emuTrigger'}  # Use a set for faster lookups
            regions = {key: [item for item in cuts if item not in elements_to_remove] for key, cuts in regions.items()}

        # Process signal samples
        if process == "Signal":
            # Check if the specified mass point is resolved
            self.check_mass_point_resolved()

            noCuts_selections = PackedSelection()

            # Apply cuts for the specified mass point if found in GenModel fields
            genmodel_field = f"WRtoNLtoLLJJ_{self._signal_sample}_TuneCP5_13TeV_madgraph_pythia8"
            if genmodel_field in events.GenModel.fields:
                selections.add(self._signal_sample, getattr(events.GenModel, genmodel_field) == 1)
                noCuts_selections.add(self._signal_sample, getattr(events.GenModel, genmodel_field) == 1)
            else:
                raise ValueError(f"Mass point '{self._signal_sample}' not found in GenModel fields.")

            noCuts_regions = {
                'WR_EE_150mll': [self._signal_sample],
                'WR_MuMu_150mll': [self._signal_sample],
                'WR_EMu_150mll': [self._signal_sample],
            }

            # Append the mass point to all region cuts
            for region, region_cuts in regions.items():
                region_cuts.append(self._signal_sample)

            for region, cuts in noCuts_regions.items():
                cut = noCuts_selections.all(*cuts)
                output['event_weight'].fill(process=process,region=region,event_weight=ak.full_like(weights.weight()[cut], 0.5),weight=weights.weight()[cut])

        # Fill histogram
        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            self.fill_basic_histograms(output, region, cut, process, AK4Jets, tightLeptons, weights)
            output['ZCand_WRCand_Mass'].fill(process=process,region=region,mass_dileptons=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).mass,mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,weight=weights.weight()[cut])

        output["weightStats"] = weights.weightStatistics
        return output

    def postprocess(self, accumulator):
        return accumulator
