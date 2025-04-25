from coffea import processor
from coffea.analysis_tools import Weights, PackedSelection
from coffea.lumi_tools import LumiData, LumiMask, LumiList
import awkward as ak
import hist.dask as dah
import hist
import numpy as np
import re
import time
import logging
import warnings
import dask_awkward as dak
warnings.filterwarnings("ignore",module="coffea.*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point=None):
        self._signal_sample = mass_point

        self.make_output = lambda: {
            'Lepton_0_Pt': self.create_hist('pt_leadlep', 'process', 'region', (200, 0, 2000), r'p_{T} of the leading lepton [GeV]'),
            'Lepton_1_Pt': self.create_hist('pt_subleadlep', 'process', 'region', (200, 0, 2000), r'p_{T} of the subleading lepton [GeV]'),
#            'Jet_0_Pt': self.create_hist('pt_leadjet', 'process', 'region', (200, 0, 2000), r'p_{T} of the leading jet [GeV]'),
#            'Jet_1_Pt': self.create_hist('pt_subleadjet', 'process', 'region', (200, 0, 2000), r'p_{T} of the subleading jet [GeV]'),
            'ZCand_Mass': self.create_hist('mass_dileptons', 'process', 'region', (120, 60, 120), r'm_{ll} [GeV]'),
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
        """Select electrons."""
        tight_electrons = (events.Electron.pt > 20) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.cutBased == 3)
        return events.Electron[tight_electrons]

    def selectMuons(self, events):
        """Select muons."""
        tight_muons = (events.Muon.pt > 20) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.tightId) & (events.Muon.tkIsoId == 2)
        return events.Muon[tight_muons]

    def fill_basic_histograms(self, output, region, cut,  process, jets, leptons, weights):
        """Helper function to fill histograms dynamically."""
        # Define a list of variables and their corresponding histograms
        variables = [
            ('Lepton_0_Pt', leptons[:, 0].pt, 'pt_leadlep'),
            ('Lepton_1_Pt', leptons[:, 1].pt, 'pt_subleadlep'),
#            ('Jet_0_Pt', jets[:, 0].pt, 'pt_leadjet'),
#            ('Jet_1_Pt', jets[:, 1].pt, 'pt_subleadjet'),
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
        mc_campaign = metadata["era"]
        process = metadata["physics_group"]
        dataset = metadata["dataset"]
        isRealData = not hasattr(events, "genWeight")
        isMC = hasattr(events, "genWeight")

        logger.info(f"Analyzing {len(events)} {dataset} events!")
        if isRealData:
            if mc_campaign == "RunIISummer20UL18":
                lumi_mask = LumiMask("data/lumis/RunII/2018/RunIISummer20UL18/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt")
            elif mc_campaign == "Run3Summer22":
                lumi_mask = LumiMask("data/lumis/Run3/2022/Run3Summer22/Cert_Collisions2022_355100_362760_Golden.txt")
            events = events[lumi_mask(events.run, events.luminosityBlock)]
#            num_events_after_mask = len(events["run"].compute())  # Compute using a lightweight branch
#            lumi_list = LumiList(events.run, events.luminosityBlock)
#            lumi_data = LumiData(f"data/lumis/Run3/2022/Run3Summer22/lumi2022.csv", is_inst_lumi=False)
#            lumi = lumi_data.get_lumi(lumi_list)
#            print(lumi.compute())

        output['mc_campaign'] = mc_campaign
        output['process'] = process
        output['dataset'] = dataset
        if not isRealData:
            output['x_sec'] = events.metadata["xsec"] 

        # Object selection
        tightElectrons = self.selectElectrons(events)
        nTightElectrons = ak.num(tightElectrons)

        tightMuons = self.selectMuons(events)
        nTightMuons = ak.num(tightMuons)

        # Event variables
        tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons = ak.pad_none(tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)], 2, axis=1)

        mll = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1]).mass, False)

        # Event selections
        selections = PackedSelection()
        selections.add("twoTightLeptons", (ak.num(tightElectrons) + ak.num(tightMuons)) == 2)

        # Trigger selections
        eTrig = events.HLT.Ele27_WPTight_Gsf | events.HLT.Ele32_WPTight_Gsf | events.HLT.Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ
        muTrig = events.HLT.IsoMu24 | events.HLT.IsoMu27 | events.HLT.Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8
        selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
        selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))

        # Event Weights
        weights = Weights(size=None, storeIndividual=True)
        if isMC:
            eventWeight = events.genWeight
            unqiue_gensumws = np.unique(events.genEventSumw.compute())
            output['sumw'] = np.sum(unqiue_gensumws)
        elif isRealData:
            eventWeight = abs(np.sign(events.event))
        weights.add("event_weight", weight=eventWeight)

        # Channel selections
        selections.add("ee", ((nTightElectrons == 2) & (nTightMuons == 0)))
        selections.add("mumu", ((nTightElectrons == 0) & (nTightMuons == 2)))

        # Jet selections
        selections.add("pt20", (tightLeptons[:, 0].pt > 20) & (tightLeptons[:, 1].pt > 20))
        selections.add("pt30", (tightLeptons[:, 0].pt > 30) & (tightLeptons[:, 1].pt > 30))
        selections.add("pt40", (tightLeptons[:, 0].pt > 40) & (tightLeptons[:, 1].pt > 40))
        selections.add("pt50", (tightLeptons[:, 0].pt > 50) & (tightLeptons[:, 1].pt > 50))
        selections.add("pt60", (tightLeptons[:, 0].pt > 60) & (tightLeptons[:, 1].pt > 60))

        # mll selections
        selections.add("60mll120", ((mll > 60) & (mll < 120)))

        # Define analysis regions
        regions = {
            'EE_DYCR_PT20':   ['twoTightLeptons', '60mll120', 'ee', 'eeTrigger', 'pt20'],
            'EE_DYCR_PT30':   ['twoTightLeptons', '60mll120', 'ee', 'eeTrigger', 'pt30'],
            'EE_DYCR_PT40':   ['twoTightLeptons', '60mll120', 'ee', 'eeTrigger', 'pt40'],
            'EE_DYCR_PT50':   ['twoTightLeptons', '60mll120', 'ee', 'eeTrigger', 'pt50'],
            'EE_DYCR_PT60':   ['twoTightLeptons', '60mll120', 'ee', 'eeTrigger', 'pt60'],
            'MuMu_DYCR_PT20': ['twoTightLeptons', '60mll120', 'mumu', 'mumuTrigger', 'pt20'],
            'MuMu_DYCR_PT30': ['twoTightLeptons', '60mll120', 'mumu', 'mumuTrigger', 'pt30'],
            'MuMu_DYCR_PT40': ['twoTightLeptons', '60mll120', 'mumu', 'mumuTrigger', 'pt40'],
            'MuMu_DYCR_PT50': ['twoTightLeptons', '60mll120', 'mumu', 'mumuTrigger', 'pt50'],
            'MuMu_DYCR_PT60': ['twoTightLeptons', '60mll120', 'mumu', 'mumuTrigger', 'pt60'],
        }

        # Fill histogram
        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            self.fill_basic_histograms(output, region, cut, process, events.Jet, tightLeptons, weights)

        output["weightStats"] = weights.weightStatistics
        return output

    def postprocess(self, accumulator):
        return accumulator
