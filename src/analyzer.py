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
import json
import dask
import dask_awkward as dak
from scipy.stats import truncnorm
import pandas as pd
warnings.filterwarnings("ignore",module="coffea.*")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point=None):
        self._signal_sample = mass_point

        self.make_output = lambda: {
            'Lepton_0_Pt': self.create_hist('pt_leadlep', 'process', 'region', (200, 0, 2000), r'p_{T} of the leading lepton [GeV]'),
            'Lepton_0_Px': self.create_hist('px_leadlep', 'process', 'region', (400, -2000, 2000), r'p_{x} of the leading lepton [GeV]'),
            'Lepton_0_Py': self.create_hist('py_leadlep', 'process', 'region', (400, -2000, 2000), r'p_{y} of the leading lepton [GeV]'),
            'Lepton_0_Pz': self.create_hist('pz_leadlep', 'process', 'region', (400, -2000, 2000), r'p_{z} of the leading lepton [GeV]'),
            'Lepton_0_Eta': self.create_hist('eta_leadlep', 'process', 'region', (60, -3, 3), r'#eta of the leading lepton'),
            'Lepton_0_Phi': self.create_hist('phi_leadlep', 'process', 'region', (80, -4, 4), r'#phi of the leading lepton'),

            'Lepton_1_Pt': self.create_hist('pt_subleadlep', 'process', 'region', (200, 0, 2000), r'p_{T} of the subleading lepton [GeV]'),
            'Lepton_1_Px': self.create_hist('px_subleadlep', 'process', 'region', (400, -2000, 2000), r'p_{x} of the subleading lepton [GeV]'),
            'Lepton_1_Py': self.create_hist('py_subleadlep', 'process', 'region', (400, -2000, 2000), r'p_{y} of the subleading lepton [GeV]'),
            'Lepton_1_Pz': self.create_hist('pz_subleadlep', 'process', 'region', (400, -2000, 2000), r'p_{z} of the subleading lepton [GeV]'),
            'Lepton_1_Eta': self.create_hist('eta_subleadlep', 'process', 'region', (60, -3, 3), r'#eta of the subleading lepton'),
            'Lepton_1_Phi': self.create_hist('phi_subleadlep', 'process', 'region', (80, -4, 4), r'#phi of the subleading lepton'),

            'Jet_0_Pt': self.create_hist('pt_leadjet', 'process', 'region', (200, 0, 2000), r'p_{T} of the leading jet [GeV]'),
            'Jet_0_Px': self.create_hist('px_leadjet', 'process', 'region', (400, -2000, 2000), r'p_{x} of the leading jet [GeV]'),
            'Jet_0_Py': self.create_hist('py_leadjet', 'process', 'region', (400, -2000, 2000), r'p_{y} of the leading jet [GeV]'),
            'Jet_0_Pz': self.create_hist('pz_leadjet', 'process', 'region', (400, -2000, 2000), r'p_{z} of the leading jet [GeV]'),
            'Jet_0_Eta': self.create_hist('eta_leadjet', 'process', 'region', (60, -3, 3), r'#eta of the leading jet'),
            'Jet_0_Phi': self.create_hist('phi_leadjet', 'process', 'region', (80, -4, 4), r'#phi of the leading jet'),

            'Jet_1_Pt': self.create_hist('pt_subleadjet', 'process', 'region', (200, 0, 2000), r'p_{T} of the subleading jet [GeV]'),
            'Jet_1_Px': self.create_hist('px_subleadjet', 'process', 'region', (400, -2000, 2000), r'p_{x} of the subleading jet [GeV]'),
            'Jet_1_Py': self.create_hist('py_subleadjet', 'process', 'region', (400, -2000, 2000), r'p_{y} of the subleading jet [GeV]'),
            'Jet_1_Pz': self.create_hist('pz_subleadjet', 'process', 'region', (400, -2000, 2000), r'p_{z} of the subleading jet [GeV]'),
            'Jet_1_Eta': self.create_hist('eta_subleadjet', 'process', 'region', (60, -3, 3), r'#eta of the subleading jet'),
            'Jet_1_Phi': self.create_hist('phi_subleadjet', 'process', 'region', (80, -4, 4), r'#phi of the subleading jet'),

            'ZCand_Mass': self.create_hist('mass_dileptons', 'process', 'region', (500, 0, 5000), r'm_{ll} [GeV]'),
            'ZCand_Pt': self.create_hist('pt_dileptons', 'process', 'region', (500, 0, 5000), r'p^{T}_{ll} [GeV]'),
            'ZCand_Px': self.create_hist('px_dileptons', 'process', 'region', (1000, -5000, 5000), r'p^{x}_{ll} [GeV]'),
            'ZCand_Py': self.create_hist('py_dileptons', 'process', 'region', (1000, -5000, 5000), r'p^{y}_{ll} [GeV]'),
            'ZCand_Pz': self.create_hist('pz_dileptons', 'process', 'region', (1000, -5000, 5000), r'p^{z}_{ll} [GeV]'),

            'Dijet_Mass': self.create_hist('mass_dijet', 'process', 'region', (500, 0, 5000), r'm_{jj} [GeV]'),
            'Dijet_Pt': self.create_hist('pt_dijet', 'process', 'region', (500, 0, 5000), r'p^{T}_{jj} [GeV]'),
            'Dijet_Px': self.create_hist('px_dijet', 'process', 'region', (1000, -5000, 5000), r'p^{x}_{jj} [GeV]'),
            'Dijet_Py': self.create_hist('py_dijet', 'process', 'region', (1000, -5000, 5000), r'p^{y}_{jj} [GeV]'),
            'Dijet_Pz': self.create_hist('pz_dijet', 'process', 'region', (1000, -5000, 5000), r'p^{z}_{jj} [GeV]'),

            'NCand_Lepton_0_Mass': self.create_hist('mass_threeobject_leadlep', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),
            'NCand_Lepton_0_Pt': self.create_hist('pt_threeobject_leadlep', 'process', 'region', (800, 0, 8000), r'p^{T}_{ljj} [GeV]'),
            'NCand_Lepton_0_Px': self.create_hist('px_threeobject_leadlep', 'process', 'region', (1600, -8000, 8000), r'p^{x}_{ljj} [GeV]'),
            'NCand_Lepton_0_Py': self.create_hist('py_threeobject_leadlep', 'process', 'region', (1600, -8000, 8000), r'p^{y}_{ljj} [GeV]'),
            'NCand_Lepton_0_Pz': self.create_hist('pz_threeobject_leadlep', 'process', 'region', (1600, -8000, 8000), r'p^{z}_{ljj} [GeV]'),

            'NCand_Lepton_1_Mass': self.create_hist('mass_threeobject_subleadlep', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),
            'NCand_Lepton_1_Pt': self.create_hist('pt_threeobject_subleadlep', 'process', 'region', (800, 0, 8000), r'p^{T}_{ljj} [GeV]'),
            'NCand_Lepton_1_Px': self.create_hist('px_threeobject_subleadlep', 'process', 'region', (1600, -8000, 8000), r'p^{x}_{ljj} [GeV]'),
            'NCand_Lepton_1_Py': self.create_hist('py_threeobject_subleadlep', 'process', 'region', (1600, -8000, 8000), r'p^{y}_{ljj} [GeV]'),
            'NCand_Lepton_1_Pz': self.create_hist('pz_threeobject_subleadlep', 'process', 'region', (1600, -8000, 8000), r'p^{z}_{ljj} [GeV]'),

            'WRCand_Mass': self.create_hist('mass_fourobject', 'process', 'region', (800, 0, 8000), r'm_{lljj} [GeV]'),
            'WRCand_Pt': self.create_hist('pt_fourobject', 'process', 'region', (800, 0, 8000), r'p^{T}_{lljj} [GeV]'),
            'WRCand_Px': self.create_hist('px_fourobject', 'process', 'region', (1600, -8000, 8000), r'p^{x}_{lljj} [GeV]'),
            'WRCand_Py': self.create_hist('py_fourobject', 'process', 'region', (1600, -8000, 8000), r'p^{y}_{lljj} [GeV]'),
            'WRCand_Pz': self.create_hist('pz_fourobject', 'process', 'region', (1600, -8000, 8000), r'p^{z}_{lljj} [GeV]'),

            'NCand_Lepton_0_Mass_Wprime': self.create_hist('mass_threeobject_leadlep_Wprime', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),    #x' aligned with l_W
            'NCand_Lepton_1_Mass_Wprime': self.create_hist('mass_threeobject_subleadlep_Wprime', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'), #x' aligned with l_W

            'NCand_Lepton_0_Mass_threeprime': self.create_hist('mass_threeobject_leadlep_threeprime', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'),    #x' aligned with threeobject
            'NCand_Lepton_1_Mass_threeprime': self.create_hist('mass_threeobject_subleadlep_threeprime', 'process', 'region', (800, 0, 8000), r'm_{ljj} [GeV]'), #x' aligned with threeobject
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
#        ak8_jets = (events.FatJet.pt > 200) & (np.abs(events.FatJet.eta) < 2.4) & (events.FatJet.jetId == 2) & (events.FatJet.msoftdrop > 40)
        return events.Jet[ak4_jets]

    def check_mass_point_resolved(self):
        """Check if the specified mass point is a resolved sample.

        Raises:
            NotImplementedError: If MN/MWR is less than 0.2, indicating an unresolved sample.
            ValueError: If the mass point format in _signal_sample is invalid.
        """
        match = re.match(r"WR(\d+)_N(\d+)", self._signal_sample)
        if match:
            mwr, mn = int(match.group(1)), int(match.group(2))
            ratio = mn / mwr
            if ratio < 0.1:
                raise NotImplementedError(
                    f"Choose a resolved sample (MN/MWR > 0.1). For this sample, MN/MWR = {ratio:.2f}."
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
            ('Lepton_0_Pt', leptons[:, 0].pt, 'pt_leadlep'),
            ('Lepton_0_Px', leptons[:, 0].px, 'px_leadlep'),
            ('Lepton_0_Py', leptons[:, 0].py, 'py_leadlep'),
            ('Lepton_0_Pz', leptons[:, 0].pz, 'pz_leadlep'),
            ('Lepton_0_Eta', leptons[:, 0].eta, 'eta_leadlep'),
            ('Lepton_0_Phi', leptons[:, 0].phi, 'phi_leadlep'),

            ('Lepton_1_Pt', leptons[:, 1].pt, 'pt_subleadlep'),
            ('Lepton_1_Px', leptons[:, 1].px, 'px_subleadlep'),
            ('Lepton_1_Py', leptons[:, 1].py, 'py_subleadlep'),
            ('Lepton_1_Pz', leptons[:, 1].pz, 'pz_subleadlep'),
            ('Lepton_1_Eta', leptons[:, 1].eta, 'eta_subleadlep'),
            ('Lepton_1_Phi', leptons[:, 1].phi, 'phi_subleadlep'),

            ('Jet_0_Pt', jets[:, 0].pt, 'pt_leadjet'),
            ('Jet_0_Px', jets[:, 0].px, 'px_leadjet'),
            ('Jet_0_Py', jets[:, 0].py, 'py_leadjet'),
            ('Jet_0_Pz', jets[:, 0].pz, 'pz_leadjet'),
            ('Jet_0_Eta', jets[:, 0].eta, 'eta_leadjet'),
            ('Jet_0_Phi', jets[:, 0].phi, 'phi_leadjet'),

            ('Jet_1_Pt', jets[:, 1].pt, 'pt_subleadjet'),
            ('Jet_1_Px', jets[:, 1].px, 'px_subleadjet'),
            ('Jet_1_Py', jets[:, 1].py, 'py_subleadjet'),
            ('Jet_1_Pz', jets[:, 1].pz, 'pz_subleadjet'),
            ('Jet_1_Eta', jets[:, 1].eta, 'eta_subleadjet'),
            ('Jet_1_Phi', jets[:, 1].phi, 'phi_subleadjet'),

            ('ZCand_Mass', (leptons[:, 0] + leptons[:, 1]).mass, 'mass_dileptons'),
            ('ZCand_Pt', (leptons[:, 0] + leptons[:, 1]).pt, 'pt_dileptons'),
            ('ZCand_Px', (leptons[:, 0] + leptons[:, 1]).px, 'px_dileptons'),
            ('ZCand_Py', (leptons[:, 0] + leptons[:, 1]).py, 'py_dileptons'),
            ('ZCand_Pz', (leptons[:, 0] + leptons[:, 1]).pz, 'pz_dileptons'),

            ('Dijet_Mass', (jets[:, 0] + jets[:, 1]).mass, 'mass_dijet'),
            ('Dijet_Pt', (jets[:, 0] + jets[:, 1]).pt, 'pt_dijet'),
            ('Dijet_Px', (jets[:, 0] + jets[:, 1]).px, 'px_dijet'),
            ('Dijet_Py', (jets[:, 0] + jets[:, 1]).py, 'py_dijet'),
            ('Dijet_Pz', (jets[:, 0] + jets[:, 1]).pz, 'pz_dijet'),

            ('NCand_Lepton_0_Mass', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_leadlep'),
            ('NCand_Lepton_0_Pt', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).pt, 'pt_threeobject_leadlep'),
            ('NCand_Lepton_0_Px', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).px, 'px_threeobject_leadlep'),
            ('NCand_Lepton_0_Py', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).py, 'py_threeobject_leadlep'),
            ('NCand_Lepton_0_Pz', (leptons[:, 0] + jets[:, 0] + jets[:, 1]).pz, 'pz_threeobject_leadlep'),

            ('NCand_Lepton_1_Mass', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_subleadlep'),
            ('NCand_Lepton_1_Pt', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).pt, 'pt_threeobject_subleadlep'),
            ('NCand_Lepton_1_Px', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).px, 'px_threeobject_subleadlep'),
            ('NCand_Lepton_1_Py', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).py, 'py_threeobject_subleadlep'),
            ('NCand_Lepton_1_Pz', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).pz, 'pz_threeobject_subleadlep'),

            ('WRCand_Mass', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_fourobject'),
            ('WRCand_Pt', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).pt, 'pt_fourobject'),
            ('WRCand_Px', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).px, 'px_fourobject'),
            ('WRCand_Py', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).py, 'py_fourobject'),
            ('WRCand_Pz', (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).pz, 'pz_fourobject'),

            ('NCand_Lepton_0_Mass_Wprime',
                    ((leptons[:, 0].energy            + jets[:, 0].energy            + jets[:, 1].energy           )**2 -
                    ((leptons[:, 0].px_Wprime_leadlep + jets[:, 0].px_Wprime_leadlep + jets[:, 1].px_Wprime_leadlep)**2 +
                     (leptons[:, 0].py_Wprime_leadlep + jets[:, 0].py_Wprime_leadlep + jets[:, 1].py_Wprime_leadlep)**2 +
                     (leptons[:, 0].pz                + jets[:, 0].pz                + jets[:, 1].pz               )**2))**0.5, 'mass_threeobject_leadlep_Wprime'),
            ('NCand_Lepton_1_Mass_Wprime',
                    ((leptons[:, 1].energy               + jets[:, 0].energy               + jets[:, 1].energy              )**2 -
                    ((leptons[:, 1].px_Wprime_subleadlep + jets[:, 0].px_Wprime_subleadlep + jets[:, 1].px_Wprime_subleadlep)**2 +
                     (leptons[:, 1].py_Wprime_subleadlep + jets[:, 0].py_Wprime_subleadlep + jets[:, 1].py_Wprime_subleadlep)**2 +
                     (leptons[:, 1].pz                   + jets[:, 0].pz                   + jets[:, 1].pz                  )**2))**0.5, 'mass_threeobject_subleadlep_Wprime'),

            ('NCand_Lepton_0_Mass_threeprime',
                    ((leptons[:, 0].energy                + jets[:, 0].energy                + jets[:, 1].energy               )**2 -
                    ((leptons[:, 0].px_threeprime_leadlep + jets[:, 0].px_threeprime_leadlep + jets[:, 1].px_threeprime_leadlep)**2 +
                     (leptons[:, 0].py_threeprime_leadlep + jets[:, 0].py_threeprime_leadlep + jets[:, 1].py_threeprime_leadlep)**2 +
                     (leptons[:, 0].pz                    + jets[:, 0].pz                    + jets[:, 1].pz                   )**2))**0.5, 'mass_threeobject_leadlep_threeprime'),
            ('NCand_Lepton_1_Mass_threeprime',
                    ((leptons[:, 1].energy                   + jets[:, 0].energy                   + jets[:, 1].energy                  )**2 -
                    ((leptons[:, 1].px_threeprime_subleadlep + jets[:, 0].px_threeprime_subleadlep + jets[:, 1].px_threeprime_subleadlep)**2 +
                     (leptons[:, 1].py_threeprime_subleadlep + jets[:, 0].py_threeprime_subleadlep + jets[:, 1].py_threeprime_subleadlep)**2 +
                     (leptons[:, 1].pz                       + jets[:, 0].pz                       + jets[:, 1].pz                      )**2))**0.5, 'mass_threeobject_subleadlep_threeprime'),
        ]

#        cutz = dask.compute(cut)[0]
#        true_count = 0
#        for entry in cutz:
#            if entry == True:
#                true_count += 1
#        print(f'{region} true_count: {true_count}')

        # Loop over variables and fill corresponding histograms
        for hist_name, values, axis_name in variables:
            output[hist_name].fill(
                process=process,
                region=region,
                **{axis_name: values[cut]},
                weight=weights.weight()[cut]
            )

    def print_output(self, dict0: dict, indent: str):
        for key1 in dict0.keys():
            if not isinstance(dict0[key1], dict):
                print(indent + f"{key1}:\n" + indent + f"   {dict0[key1]}")
            else:
                dict1 = dict0[key1]
                print(indent + f"{key1}:")
                self.print_output(dict1, indent + "   ")

    def get_mass_point(self):
        match = re.match(r"WR(\d+)_N(\d+)", self._signal_sample)
        if match:
            mwr, mn = int(match.group(1)), int(match.group(2))
            return mwr, mn

    def process(self, events): 
        output = self.make_output()

#        print('\nevents.fields:\n' + str(events.fields) + '\n')

#        for field in events.fields:
#            print(f'\nevents["{field}"].fields:\n' + str(events[field].fields))

        metadata = events.metadata

#        print('\nevents.metadata:\n' + str(metadata) + '\n')

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
   
        # Process signal samples
        if process == "Signal": self.check_mass_point_resolved()

        # Object selection
        tightElectrons, _  = self.selectElectrons(events)
        nTightElectrons = ak.num(tightElectrons)

        tightMuons, _ = self.selectMuons(events)
        nTightMuons = ak.num(tightMuons)

        AK4Jets = self.selectJets(events)
        nAK4Jets = ak.num(AK4Jets)

        # Event variables
        tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons = ak.pad_none(tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)], 2, axis=1)
        AK4Jets = ak.pad_none(AK4Jets, 2, axis=1)


        #calculate Wgamma
        #x' axis is always aligned with the W lepton
        #Wgamma is the angle between the W lepton's xy momentum vector and the positive CMS x-axis
        #Wgamma_leadlep is the Wgamma values assuming that the N lepton is the lead lepton
        #Wgamma_subleadlep is the Wgamma values assuming that the N lepton is the sublead lepton
        Wgamma_leadlep = np.arctan2(tightLeptons[:,1].py, tightLeptons[:,1].px)
        Wgamma_subleadlep = np.arctan2(tightLeptons[:,0].py, tightLeptons[:,0].px)


        #create the primed px of the leptons as a field of tightLeptons assuming the N lepton is the lead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.cos(Wgamma_leadlep)*tightLeptons.px + np.sin(Wgamma_leadlep)*tightLeptons.py,
                where='px_Wprime_leadlep')
        #create the primed py of the leptons as a field of tightLeptons assuming the N lepton is the lead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.sin(Wgamma_leadlep)*tightLeptons.px*(-1) + np.cos(Wgamma_leadlep)*tightLeptons.py,
                where='py_Wprime_leadlep')

        #create the primed px of the jets as a field of AK4Jets assuming the N lepton is the lead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.cos(Wgamma_leadlep)*AK4Jets.px + np.sin(Wgamma_leadlep)*AK4Jets.py,
                where='px_Wprime_leadlep')
        #create the primed py of the jets as a field of AK4Jets assuming the N lepton is the lead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.sin(Wgamma_leadlep)*AK4Jets.px*(-1) + np.cos(Wgamma_leadlep)*AK4Jets.py,
                where='py_Wprime_leadlep')


        #create the primed px of the leptons as a field of tightLeptons assuming the N lepton is the sublead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.cos(Wgamma_subleadlep)*tightLeptons.px + np.sin(Wgamma_subleadlep)*tightLeptons.py,
                where='px_Wprime_subleadlep')
        #create the primed py of the leptons as a field of tightLeptons assuming the N lepton is the sublead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.sin(Wgamma_subleadlep)*tightLeptons.px*(-1) + np.cos(Wgamma_subleadlep)*tightLeptons.py,
                where='py_Wprime_subleadlep')

        #create the primed px of the jets as a field of AK4Jets assuming the N lepton is the sublead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.cos(Wgamma_subleadlep)*AK4Jets.px + np.sin(Wgamma_subleadlep)*AK4Jets.py,
                where='px_Wprime_subleadlep')
        #create the primed py of the jets as a field of AK4Jets assuming the N lepton is the sublead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.sin(Wgamma_subleadlep)*AK4Jets.px*(-1) + np.cos(Wgamma_subleadlep)*AK4Jets.py,
                where='py_Wprime_subleadlep')


        #calculate threegamma
        #x' axis is always aligned with the threeobject (l_N, j_1, j_2)
        #threegamma is the angle between the threeobject's xy momentum vector and the positive CMS x-axis
        #threegamma_leadlep is the threegamma values assuming that the N lepton is the lead lepton
        #threegamma_subleadlep is the threegamma values assuming that the N lepton is the sublead lepton
        px_threeobj_leadlep = tightLeptons[:, 0].px + AK4Jets[:, 0].px + AK4Jets[:, 1].px
        py_threeobj_leadlep = tightLeptons[:, 0].py + AK4Jets[:, 0].py + AK4Jets[:, 1].py
        px_threeobj_subleadlep = tightLeptons[:, 1].px + AK4Jets[:, 0].px + AK4Jets[:, 1].px
        py_threeobj_subleadlep = tightLeptons[:, 1].py + AK4Jets[:, 0].py + AK4Jets[:, 1].py

        threegamma_leadlep = np.arctan2(py_threeobj_leadlep, px_threeobj_leadlep)
        threegamma_subleadlep = np.arctan2(py_threeobj_subleadlep, px_threeobj_subleadlep)

        #create the primed px of the leptons as a field of tightLeptons assuming the N lepton is the lead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.cos(threegamma_leadlep)*tightLeptons.px + np.sin(threegamma_leadlep)*tightLeptons.py,
                where='px_threeprime_leadlep')
        #create the primed py of the leptons as a field of tightLeptons assuming the N lepton is the lead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.sin(threegamma_leadlep)*tightLeptons.px*(-1) + np.cos(threegamma_leadlep)*tightLeptons.py,
                where='py_threeprime_leadlep')

        #create the primed px of the jets as a field of AK4Jets assuming the N lepton is the lead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.cos(threegamma_leadlep)*AK4Jets.px + np.sin(threegamma_leadlep)*AK4Jets.py,
                where='px_threeprime_leadlep')
        #create the primed py of the jets as a field of AK4Jets assuming the N lepton is the lead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.sin(threegamma_leadlep)*AK4Jets.px*(-1) + np.cos(threegamma_leadlep)*AK4Jets.py,
                where='py_threeprime_leadlep')


        #create the primed px of the leptons as a field of tightLeptons assuming the N lepton is the sublead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.cos(threegamma_subleadlep)*tightLeptons.px + np.sin(threegamma_subleadlep)*tightLeptons.py,
                where='px_threeprime_subleadlep')
        #create the primed py of the leptons as a field of tightLeptons assuming the N lepton is the sublead lepton
        tightLeptons = ak.with_field(tightLeptons,
                np.sin(threegamma_subleadlep)*tightLeptons.px*(-1) + np.cos(threegamma_subleadlep)*tightLeptons.py,
                where='py_threeprime_subleadlep')

        #create the primed px of the jets as a field of AK4Jets assuming the N lepton is the sublead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.cos(threegamma_subleadlep)*AK4Jets.px + np.sin(threegamma_subleadlep)*AK4Jets.py,
                where='px_threeprime_subleadlep')
        #create the primed py of the jets as a field of AK4Jets assuming the N lepton is the sublead lepton
        AK4Jets = ak.with_field(AK4Jets,
                np.sin(threegamma_subleadlep)*AK4Jets.px*(-1) + np.cos(threegamma_subleadlep)*AK4Jets.py,
                where='py_threeprime_subleadlep')

        

#        factorz = dask.compute(factors)
#        print(f'\nfactors:\n{factors}\n')
#        print(f'\ndask.compute(factors):\n{factorz}\n')
#        print(f'\ndask.compute(factors)[0]:\n{factorz[0]}\n')
#        print(f'\nlen(dask.compute(factors)[0]):\n{len(factorz[0])}\n')
#        print(f'\ndask.compute(factors)[0][0]:\n{factorz[0][0]}\n')
#        print(f'\nlen(dask.compute(factors)[0][0]):\n{len(factorz[0][0])}\n')
#
#        print(f'\ndask.compute(factors)[0][:, 0]:\n{factorz[0][:, 0]}\n')

#        factors = factors.repartition(AK4Jets.npartitions)


#        print(f'\nfactors: {factors}\n')
#        print(f'\nfactors[:, 0]: {factors[:, 0]}\n')
#        print(f'\nfactors[:, 1]: {factors[:, 1]}\n')

#        max_ind = 20
#
#        print('\n>>>>>>>>>>>>>>>>>> factors[:,0] values <<<<<<<<<<<<<<<<<<<<<<<<<<<')
#        for ind in range(0,max_ind):
#            print(f'factors[:, 0][{ind}]: {factors[:, 0][ind]}')
#
#        print('\n>>>>>>>>>>>>>>>>>> factors[:,1] values <<<<<<<<<<<<<<<<<<<<<<<<<<<')
#        for ind in range(0,max_ind):
#            print(f'factors[:, 1][{ind}]: {factors[:, 1][ind]}')



#        AK4Jetz_0 = dask.compute(AK4Jets_0)
#        AK4Jetz_1 = dask.compute(AK4Jets_1)
#
#        print(f'\nlen(dask.compute(AK4Jets[:, 0])[0]): {len(AK4Jetz_0[0])}\n')
#        print(f'\ndask.compute(AK4Jets[:, 0])[0]: {AK4Jetz_0[0]}\n')
#        print(f'\nlen(dask.compute(AK4Jets[:, 1])[0]): {len(AK4Jetz_1[0])}\n')
#        print(f'\ndask.compute(AK4Jets[:, 1])[0]: {AK4Jetz_1[0]}\n')

#        print('>>>>>>>>>>>>>>>>>> AK4Jets_0 fields <<<<<<<<<<<<<<<<<<<<<<<<<<<'')
#        for ind in range(0,5):
#            if str(type(AK4Jetz_0[0][ind])) != "<class 'NoneType'>":
#                print(f'\ndask.compute(AK4Jets[:, 0])[0][{ind}].fields:\n{AK4Jetz_0[0][ind].fields}\n')
#            else:
#                print('\nNo jet in this spot\n')
#
#        print('>>>>>>>>>>>>>>>>>> AK4Jets_1 fields <<<<<<<<<<<<<<<<<<<<<<<<<<<'')
#        for ind in range(0,5):
#            if str(type(AK4Jetz_1[0][ind])) != "<class 'NoneType'>":
#                print(f'\ndask.compute(AK4Jets[:, 1])[0][{ind}].fields:\n{AK4Jetz_1[0][ind].fields}\n')
#            else:
#                print('\nNo jet in this spot\n')

#        print('>>>>>>>>>>>>>>>>>> AK4Jets_0 px and px_gauss values <<<<<<<<<<<<<<<<<<<<<<<<<<<')
#        for ind in range(0,max_ind):
#            if str(type(AK4Jetz_0[0][ind])) != "<class 'NoneType'>":
#                print(f'\ndask.compute(AK4Jets[:, 0])[0][{ind}].px: {AK4Jetz_0[0][ind].px}\n')
#                print(f'\ndask.compute(AK4Jets[:, 0])[0][{ind}].px_gauss: {AK4Jetz_0[0][ind].px_gauss}\n')
#            else:
#                print('\nNo jet in this spot\n')
#
#        print('>>>>>>>>>>>>>>>>>> AK4Jets_1 px and px_gauss values <<<<<<<<<<<<<<<<<<<<<<<<<<<')
#        for ind in range(0,max_ind):
#            if str(type(AK4Jetz_1[0][ind])) != "<class 'NoneType'>":
#                print(f'\ndask.compute(AK4Jets[:, 1])[0][{ind}].px: {AK4Jetz_1[0][ind].px}\n')
#                print(f'\ndask.compute(AK4Jets[:, 1])[0][{ind}].px_gauss: {AK4Jetz_1[0][ind].px_gauss}\n')
#            else:
#                print('\nNo jet in this spot\n')


#        AK4Jets_0_nonecount = 0
#        AK4Jets_0_jetcount = 0
#        AK4Jets_1_nonecount = 0
#        AK4Jets_1_jetcount = 0
#
#        for ind in range(len(AK4Jetz_0[0])):
#            if str(type(AK4Jetz_0[0][ind])) == "<class 'NoneType'>":
#                AK4Jets_0_nonecount += 1
#            if str(type(AK4Jetz_0[0][ind])) == "<class 'coffea.nanoevents.methods.nanoaod.JetRecord'>":
#                AK4Jets_0_jetcount += 1
#
#        print(f'\nAK4Jets_0_nonecount: {AK4Jets_0_nonecount}\n')
#        print(f'\nAK4Jets_0_jetcount: {AK4Jets_0_jetcount}\n')
#
#        for ind in range(len(AK4Jetz_1[0])):
#            if str(type(AK4Jetz_1[0][ind])) == "<class 'NoneType'>":
#                AK4Jets_1_nonecount += 1
#            if str(type(AK4Jetz_1[0][ind])) == "<class 'coffea.nanoevents.methods.nanoaod.JetRecord'>":
#                AK4Jets_1_jetcount += 1
#
#        print(f'\nAK4Jets_1_nonecount: {AK4Jets_1_nonecount}\n')
#        print(f'\nAK4Jets_1_jetcount: {AK4Jets_1_jetcount}\n')
    


#        print(f'\npy2pt_threeobj_leadlep_Wprime: {py2pt_threeobj_leadlep_Wprime}  length: {len(py2pt_threeobj_leadlep_Wprime)}\n')
#        print(f'\npy2pt_threeobj_subleadlep_Wprime: {py2pt_threeobj_subleadlep_Wprime}  length: {len(py2pt_threeobj_subleadlep_Wprime)}\n')
#
#        print(f'\npy2pt_threeobj_leadlep_threeprime: {py2pt_threeobj_leadlep_threeprime}  length: {len(py2pt_threeobj_leadlep_threeprime)}\n')
#        print(f'\npy2pt_threeobj_subleadlep_threeprime: {py2pt_threeobj_subleadlep_threeprime}  length: {len(py2pt_threeobj_subleadlep_threeprime)}\n')
#
#        print(f'\npy2pt_gauss_threeobj_leadlep_threeprime: {py2pt_gauss_threeobj_leadlep_threeprime}  length: {len(py2pt_gauss_threeobj_leadlep_threeprime)}\n')
#        print(f'\npy2pt_gauss_threeobj_subleadlep_threeprime: {py2pt_gauss_threeobj_subleadlep_threeprime}  length: {len(py2pt_gauss_threeobj_subleadlep_threeprime)}\n')



#        AK4Jetss_0 = ak.Array([[x] if x is not None else [None] for x in AK4Jets_0])
#        AK4Jetss_1 = ak.Array([[x] if x is not None else [None] for x in AK4Jets_1])
#
#        print(f'\nAK4Jetss_0: {AK4Jetss_0}\n')
#        print(f'\nAK4Jetss_1: {AK4Jetss_1}\n')
#
#        AK4Jets = ak.concatenate((AK4Jetss_0, AK4Jetss_1), axis=1)

#        print(f'AK4Jets: {AK4Jets}')


#        tightLeptonz = dask.compute(tightLeptons)
#
#        print(f'\nlen(tightLeptons[0]): {len(tightLeptonz[0])}\n')
#
#        three_count = 0
#        two_count = 0
#        one_count = 0
#        zero_count = 0
#
#        for ind in range(0, len(tightLeptonz[0])):
##            print(f'ind: {ind}              type: {type(tightLeptonz[0][ind])}')
#            if str(type(tightLeptonz[0][ind])) != "<class 'NoneType'>":
#                if len(tightLeptonz[0][ind]) >= 3:
#                    three_count += 1
#                if (len(tightLeptonz[0][ind]) == 2) and (str(type(tightLeptonz[0][ind][1])) != "<class 'NoneType'>"):
#                    two_count += 1
#                elif (len(tightLeptonz[0][ind]) == 2) and (str(type(tightLeptonz[0][ind][0])) != "<class 'NoneType'>") and (str(type(tightLeptonz[0][ind][1])) == "<class 'NoneType'>"):
#                    one_count += 1
#                elif (len(tightLeptonz[0][ind]) == 2) and (str(type(tightLeptonz[0][ind][0])) == "<class 'NoneType'>") and (str(type(tightLeptonz[0][ind][1])) == "<class 'NoneType'>"):
#                    zero_count += 1
#            else:
#                zero_count += 1
#        print(f'\nNo. events w/ 3 or more leps: {three_count}\n')
#        print(f'\nNo. events w/ 2 leps: {two_count}\n')
#        print(f'\nNo. events w/ 1 lep: {one_count}\n')
#        print(f'\nNo. events w/ 0 leps: {zero_count}\n')
#       
#        for ind in range(0,5):
##            if str(type(tightLeptonz[0][ind])) != "<class 'NoneType'>":
##                if (hasattr(tightLeptonz[0][ind][0], 'deltaEtaSC') and hasattr(tightLeptonz[0][ind][1], 'tkRelIso')) or (hasattr(tightLeptonz[0][ind][1], 'deltaEtaSC') and hasattr(tightLeptonz[0][ind][0], 'tkRelIso')):
##                if (hasattr(tightLeptonz[0][ind][0], 'deltaEtaSC'):
##                if (hasattr(tightLeptonz[0][ind][0], 'tkRelIso')):
#
#                print(f'>>>>>>>>>>>>>>>>>> Event No. {ind} <<<<<<<<<<<<<<<<<<<<<')
#
#                print('\ntype(tightLeptons) uncomputed:\n' + str(type(tightLeptons)) + '\n')
#                print('\ntightLeptons uncomputed:\n' + str(tightLeptons) + '\n')
#
#                print('\ntype(tightLeptons):\n' + str(type(tightLeptonz[0])) + '\n')
#                print('\ntightLeptons:\n' + str(tightLeptonz[0]) + '\n')
#
#                print(f'\ntightLeptons[{ind}]:\n' + str(tightLeptonz[0][ind]) + '\n')
#
#                if str(type(tightLeptonz[0][ind])) != "<class 'NoneType'>":
#                    for particle in tightLeptonz[0][ind]:
#                        print('\ntype(particle): ' + str(type(particle)) + '\n')
#
#                    for particle in tightLeptonz[0][ind]:
#                        if str(type(particle)) != "<class 'NoneType'>":
#                            print('\nparticle.fields: ' + str(particle.fields) + '\n')
#                        else:
#                            print('particle.fields: no fields\n')
#
#                    for particle in tightLeptonz[0][ind]:
#                        if str(type(particle)) != "<class 'NoneType'>":
#                            for field in particle.fields:
#                                print(f"{field}: " + str(particle[str(field)]))
#                            if particle.px >= 0:
#                                print('gamma (calc): ' + str(np.arctan(particle.py/particle.px)))
#                            else:
#                                print('gamma (calc): ' + str(np.arctan(particle.py/particle.px) + np.pi))
#                            print()
#                        else:
#                            print('no fields: no data\n')
#                else:
#                    print('no leptons in this event')
#
#                print('---------------------------------------------------------------------------------------------------')


#        AK4Jetz = dask.compute(AK4Jets)
#
#        print(f'\nlen(AK4Jets[0]): {len(AK4Jetz[0])}\n')
#
#        three_count = 0
#        two_count = 0
#        one_count = 0
#        zero_count = 0
#
#        for ind in range(0, len(AK4Jetz[0])):
##            print(f'ind: {ind}              type: {type(AK4Jetz[0][ind])}')
#            if str(type(AK4Jetz[0][ind])) != "<class 'NoneType'>":
#                if len(AK4Jetz[0][ind]) >= 3:
#                    three_count += 1
#                if (len(AK4Jetz[0][ind]) == 2) and (str(type(AK4Jetz[0][ind][1])) != "<class 'NoneType'>"):
#                    two_count += 1
#                elif (len(AK4Jetz[0][ind]) == 2) and (str(type(AK4Jetz[0][ind][0])) != "<class 'NoneType'>") and (str(type(AK4Jetz[0][ind][1])) == "<class 'NoneType'>"):
#                    one_count += 1
#                elif (len(AK4Jetz[0][ind]) == 2) and (str(type(AK4Jetz[0][ind][0])) == "<class 'NoneType'>") and (str(type(AK4Jetz[0][ind][1])) == "<class 'NoneType'>"):
#                    zero_count += 1
#            else:
#                zero_count += 1
#        print(f'\nNo. events w/ 3 or more jets: {three_count}\n')
#        print(f'\nNo. events w/ 2 jets: {two_count}\n')
#        print(f'\nNo. events w/ 1 jet: {one_count}\n')
#        print(f'\nNo. events w/ 0 jets: {zero_count}\n')
#
#        for ind in range(0,5):
#
#                print(f'>>>>>>>>>>>>>>>>>> Event No. {ind} <<<<<<<<<<<<<<<<<<<<<')
#
#                print('\ntype(AK4Jets) uncomputed:\n' + str(type(AK4Jets)) + '\n')
#                print('\nAK4Jets uncomputed:\n' + str(AK4Jets) + '\n')
#                print('\ndask.compute(AK4Jets):\n' + str(AK4Jetz) + '\n')
#
#                print('\ntype(AK4Jets):\n' + str(type(AK4Jetz[0])) + '\n')
#                print('\nAK4Jets:\n' + str(AK4Jetz[0]) + '\n')
#
#                print(f'\nAK4Jets[{ind}]:\n' + str(AK4Jetz[0][ind]) + '\n')
#
#                if str(type(AK4Jetz[0][ind])) != "<class 'NoneType'>":
#                    for particle in AK4Jetz[0][ind]:
#                        print('\ntype(particle): ' + str(type(particle)) + '\n')
#
#                    for particle in AK4Jetz[0][ind]:
#                        if str(type(particle)) != "<class 'NoneType'>":
#                            print('\nparticle.fields: ' + str(particle.fields) + '\n')
#                        else:
#                            print('particle.fields: no fields\n')
#
#                    for particle in AK4Jetz[0][ind]:
#                        if str(type(particle)) != "<class 'NoneType'>":
#                            for field in particle.fields:
#                                print(f"{field}: " + str(particle[str(field)]))
#                            print()
#                        else:
#                            print('no fields: no data\n')
#                else:
#                    print("no jets in this event")
#
#                print('---------------------------------------------------------------------------------------------------')


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
            output['sumw'] = ak.sum(eventWeight) if process == "Signal" else events.metadata["genEventSumw"]
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

        # Cutflow Tables
        selections.add("leadJetPt500", (ak.any(AK4Jets.pt > 500, axis=1)))
        electron_cutflow = selections.cutflow("leadJetPt500", "eejj", "eeTrigger", "minTwoAK4Jets", 'dr>0.4', 'mlljj>800', '400mll')
        muon_cutflow = selections.cutflow("leadJetPt500", "mumujj", "mumuTrigger", "minTwoAK4Jets", 'dr>0.4', 'mlljj>800', '400mll')
#        print(electron_cutflow.print())
#        print(muon_cutflow.print())

        # Define analysis regions
        regions = {
            'WR_EE_Resolved_DYCR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
            'WR_MuMu_Resolved_DYCR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
            'WR_EMu_Resolved_CR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
            'WR_EE_Resolved_SR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'WR_MuMu_Resolved_SR': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],
        }

        # Blind signal region and remove triggers
        if isRealData:
            # Remove specific regions
            for region in ['WR_EE_Resolved_DYSR', 'WR_MuMu_Resolved_DYSR']:
                regions.pop(region, None)  # Use pop with a default to avoid KeyError

            # Remove triggers from all remaining regions
            elements_to_remove = {'mumuTrigger', 'eeTrigger', 'emuTrigger'}  # Use a set for faster lookups
            regions = {key: [item for item in cuts if item not in elements_to_remove] for key, cuts in regions.items()}

        # Fill histogram
        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            self.fill_basic_histograms(output, region, cut, process, AK4Jets, tightLeptons, weights)








        # Get cut events for ee channel
        ee_cuts = regions['WR_EE_Resolved_SR']
        ee_cut = selections.all(*ee_cuts)                # both ee and mumu cuts have ~150 more True values than the number of events in the final ROOT histograms
        mumu_cuts = regions['WR_MuMu_Resolved_SR']
        mumu_cut = selections.all(*mumu_cuts)

#        cutz = dask.compute(cut)[0]
#        print(f'cut: {cutz}')
#        true_count = 0
#        for value in cutz:
#            if value == True:
#                true_count += 1
#        print(f'num True: {true_count}')

        AK4Jets_ee   = AK4Jets[ee_cut]
        AK4Jets_mumu = AK4Jets[mumu_cut]
        tightLeptons_ee   = tightLeptons[ee_cut]
        tightLeptons_mumu = tightLeptons[mumu_cut]

        AK4Jetz_ee   = dask.compute(AK4Jets_ee)[0]
        AK4Jetz_mumu = dask.compute(AK4Jets_mumu)[0]
        tightLeptonz_ee   = dask.compute(tightLeptons_ee)[0]
        tightLeptonz_mumu = dask.compute(tightLeptons_mumu)[0]

#        def check_for_extras(array):
#            extra_count = 0
#            for event in array:
#                if len(event) >= 3:
#                    extra_count += 1
#            return extra_count
#
#        print(f'AK4Jets_ee extra count: {check_for_extras(AK4Jetz_ee)}\n')
#        print(f'AK4Jets_mumu extra count: {check_for_extras(AK4Jetz_mumu)}\n')
#        print(f'tightLeptons_ee extra count: {check_for_extras(tightLeptonz_ee)}\n')
#        print(f'tightLeptons_mumu extra count: {check_for_extras(tightLeptonz_mumu)}\n')

#        print(f'len(AK4Jets_ee): {len(AK4Jetz_ee)}')
#        print(f'len(AK4Jets_mumu): {len(AK4Jetz_mumu)}')
#        print(f'len(tightLeptons_ee): {len(tightLeptonz_ee)}')
#        print(f'len(tightLeptons_mumu): {len(tightLeptonz_mumu)}')

#        print(f'AK4Jets_ee: {AK4Jetz_ee}')
#        print(f'AK4Jets_mumu: {AK4Jetz_mumu}')
#        print(f'tightLeptons_ee: {tightLeptonz_ee}')
#        print(f'tightLeptons_mumu: {tightLeptonz_mumu}')
#
#        print(f'AK4Jets_ee[0]: {AK4Jetz_ee[0]}')
#        print(f'AK4Jets_mumu[0]: {AK4Jetz_mumu[0]}')
#        print(f'tightLeptons_ee[0]: {tightLeptonz_ee[0]}')
#        print(f'tightLeptons_mumu[0]: {tightLeptonz_mumu[0]}')

#        print(f'AK4Jets_ee: {type(AK4Jetz_ee[0][0])}')
#        print(f'AK4Jets_mumu: {type(AK4Jetz_mumu[0][0])}')
#        print(f'tightLeptons_ee: {type(tightLeptonz_ee[0][0])}')
#        print(f'tightLeptons_mumu: {type(tightLeptonz_mumu[0][0])}')

#        pt_threeobj_leadlep    = (tightLeptons_ee[:, 0] + AK4Jets_ee[:, 0] + AK4Jets_ee[:, 1]).pt
#        pt_threeobj_subleadlep = (tightLeptons_ee[:, 1] + AK4Jets_ee[:, 0] + AK4Jets_ee[:, 1]).pt
#
#        py2pt_threeobj_leadlep_Wprime    = (tightLeptons_ee[:, 0].py_Wprime_leadlep +
#                                                 AK4Jets_ee[:, 0].py_Wprime_leadlep +
#                                                 AK4Jets_ee[:, 1].py_Wprime_leadlep)/pt_threeobj_leadlep
#
#        py2pt_threeobj_subleadlep_Wprime = (tightLeptons_ee[:, 1].py_Wprime_subleadlep +
#                                                 AK4Jets_ee[:, 0].py_Wprime_subleadlep +
#                                                 AK4Jets_ee[:, 1].py_Wprime_subleadlep)/pt_threeobj_subleadlep
#
#        py2pt_threeobj_leadlep_threeprime    = (tightLeptons_ee[:, 0].py_threeprime_leadlep +
#                                                     AK4Jets_ee[:, 0].py_threeprime_leadlep +
#                                                     AK4Jets_ee[:, 1].py_threeprime_leadlep)/pt_threeobj_leadlep
#
#        py2pt_threeobj_subleadlep_threeprime = (tightLeptons_ee[:, 1].py_threeprime_subleadlep +
#                                                     AK4Jets_ee[:, 0].py_threeprime_subleadlep +
#                                                     AK4Jets_ee[:, 1].py_threeprime_subleadlep)/pt_threeobj_subleadlep
#
#        py2pt_gauss_threeobj_leadlep_threeprime    = (tightLeptons_ee[:, 0].py_threeprime_leadlep +
#                                                               AK4Jets_0.py_gauss_threeprime_leadlep +
#                                                               AK4Jets_1.py_gauss_threeprime_leadlep)/pt_threeobj_leadlep
#
#        py2pt_gauss_threeobj_subleadlep_threeprime = (tightLeptons_ee[:, 1].py_threeprime_subleadlep +
#                                                               AK4Jets_0.py_gauss_threeprime_subleadlep +
#                                                               AK4Jets_1.py_gauss_threeprime_subleadlep)/pt_threeobj_subleadlep
##------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##        pt_threeobj_leadlep    = ak.Array(dask.compute(pt_threeobj_leadlep)[0])
##        pt_threeobj_subleadlep = ak.Array(dask.compute(pt_threeobj_subleadlep)[0])
#
#        py2pt_threeobj_leadlep_Wprime    = dask.compute(py2pt_threeobj_leadlep_Wprime)[0].tolist()
#        py2pt_threeobj_subleadlep_Wprime = dask.compute(py2pt_threeobj_subleadlep_Wprime)[0].tolist()
#
#        py2pt_threeobj_leadlep_threeprime    = dask.compute(py2pt_threeobj_leadlep_threeprime)[0].tolist()
#        py2pt_threeobj_subleadlep_threeprime = dask.compute(py2pt_threeobj_subleadlep_threeprime)[0].tolist()
#
#        py2pt_gauss_threeobj_leadlep_threeprime    = dask.compute(py2pt_gauss_threeobj_leadlep_threeprime)[0].tolist()
#        py2pt_gauss_threeobj_subleadlep_threeprime = dask.compute(py2pt_gauss_threeobj_subleadlep_threeprime)[0].tolist()
#
#        threeobj_data = {
#                'py2pt_threeobj_leadlep_Wprime': py2pt_threeobj_leadlep_Wprime,
#                'py2pt_threeobj_subleadlep_Wprime': py2pt_threeobj_subleadlep_Wprime,
#                'py2pt_threeobj_leadlep_threeprime': py2pt_threeobj_leadlep_threeprime,
#                'py2pt_threeobj_subleadlep_threeprime': py2pt_threeobj_subleadlep_threeprime,
#                'py2pt_gauss_threeobj_leadlep_threeprime': py2pt_gauss_threeobj_leadlep_threeprime,
#                'py2pt_gauss_threeobj_subleadlep_threeprime': py2pt_gauss_threeobj_subleadlep_threeprime,
#                }

        AK4Jets_ee_px_0 = AK4Jetz_ee.px[:, 0].tolist()
        AK4Jets_ee_px_1 = AK4Jetz_ee.px[:, 1].tolist()
        AK4Jets_ee_py_0 = AK4Jetz_ee.py[:, 0].tolist()
        AK4Jets_ee_py_1 = AK4Jetz_ee.py[:, 1].tolist()

        AK4Jets_mumu_px_0 = AK4Jetz_mumu.px[:, 0].tolist()
        AK4Jets_mumu_px_1 = AK4Jetz_mumu.px[:, 1].tolist()
        AK4Jets_mumu_py_0 = AK4Jetz_mumu.py[:, 0].tolist()
        AK4Jets_mumu_py_1 = AK4Jetz_mumu.py[:, 1].tolist()

        tightLeptons_ee_px_0 = tightLeptonz_ee.px[:, 0].tolist()
        tightLeptons_ee_px_1 = tightLeptonz_ee.px[:, 1].tolist()
        tightLeptons_ee_py_0 = tightLeptonz_ee.py[:, 0].tolist()
        tightLeptons_ee_py_1 = tightLeptonz_ee.py[:, 1].tolist()

        tightLeptons_mumu_px_0 = tightLeptonz_mumu.px[:, 0].tolist()
        tightLeptons_mumu_px_1 = tightLeptonz_mumu.px[:, 1].tolist()
        tightLeptons_mumu_py_0 = tightLeptonz_mumu.py[:, 0].tolist()
        tightLeptons_mumu_py_1 = tightLeptonz_mumu.py[:, 1].tolist()

        obj_data_list = [
                AK4Jets_ee_px_0,
                AK4Jets_ee_px_1,
                AK4Jets_ee_py_0,
                AK4Jets_ee_py_1,

                AK4Jets_mumu_px_0,
                AK4Jets_mumu_px_1,
                AK4Jets_mumu_py_0,
                AK4Jets_mumu_py_1,

                tightLeptons_ee_px_0,
                tightLeptons_ee_px_1,
                tightLeptons_ee_py_0,
                tightLeptons_ee_py_1,

                tightLeptons_mumu_px_0,
                tightLeptons_mumu_px_1,
                tightLeptons_mumu_py_0,
                tightLeptons_mumu_py_1,
                ]

        max_len = 0
        for datalist in obj_data_list:
            if len(datalist) > max_len:
                max_len = len(datalist)
        for datalist in obj_data_list:
            while len(datalist) < max_len:
                datalist.append(99999999.9)

        obj_data = {
                'AK4Jets_ee_px_0': ak.Array(obj_data_list[0]),
                'AK4Jets_ee_px_1': ak.Array(obj_data_list[1]),
                'AK4Jets_ee_py_0': ak.Array(obj_data_list[2]),
                'AK4Jets_ee_py_1': ak.Array(obj_data_list[3]),

                'AK4Jets_mumu_px_0': ak.Array(obj_data_list[4]),
                'AK4Jets_mumu_px_1': ak.Array(obj_data_list[5]),
                'AK4Jets_mumu_py_0': ak.Array(obj_data_list[6]),
                'AK4Jets_mumu_py_1': ak.Array(obj_data_list[7]),

                'tightLeptons_ee_px_0': ak.Array(obj_data_list[8]),
                'tightLeptons_ee_px_1': ak.Array(obj_data_list[9]),
                'tightLeptons_ee_py_0': ak.Array(obj_data_list[10]),
                'tightLeptons_ee_py_1': ak.Array(obj_data_list[11]),

                'tightLeptons_mumu_px_0': ak.Array(obj_data_list[12]),
                'tightLeptons_mumu_px_1': ak.Array(obj_data_list[13]),
                'tightLeptons_mumu_py_0': ak.Array(obj_data_list[14]),
                'tightLeptons_mumu_py_1': ak.Array(obj_data_list[15]),
                }

#        print('---------------------------------------------------------------------------------------------------------------------------')
#        for key, value in threeobj_data.items():
#            print(f'{key}: [{value[0]}, {value[1]}, {value[2]}, {value[3]}, {value[4]}, {value[5]}, {value[6]}]\n')

        save_path = '/local/cms/user/poczo001/fff/WrCoffea/CSVs'

        obj_dataframe = pd.DataFrame(obj_data)

        if process == "Signal":
            mass_Wr, mass_N = self.get_mass_point()

        obj_dataframe.to_csv(f'{save_path}/object_data_mWr_{mass_Wr}_mN_{mass_N}.csv', index=False)
        print(f'\nsaved csv file to {save_path}\n')










        output["weightStats"] = weights.weightStatistics

#        print('output.items():')
#        for pair in output.items():
#            print(str(pair))
#            print(type(pair[0]))

#        print('\n' + str(dataset) + ' output:\n')
#        self.print_output(output, "")
#        print()

        return output

    def postprocess(self, accumulator):
        return accumulator
