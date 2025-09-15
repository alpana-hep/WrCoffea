from coffea import processor
from coffea.analysis_tools import Weights, PackedSelection
from coffea.lumi_tools import LumiMask
from coffea.lookup_tools.dense_lookup import dense_lookup
import awkward as ak
import hist
import numpy as np
import os
import re
import logging
import warnings
import json

warnings.filterwarnings("ignore", module="coffea.*")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _minimal_repeated_unit(s: str) -> str:
    """
    Heuristic: find the smallest substring which, when repeated, can reconstruct s.
    If none obvious, return s itself.
    """
    if not isinstance(s, str) or len(s) == 0:
        return s
    for size in range(1, len(s) // 2 + 1):
        if len(s) % size != 0:
            continue
        unit = s[:size]
        if unit * (len(s) // size) == s:
            return unit
    return s  # fallback


class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point, sf_file=None):
        self._signal_sample = mass_point

        self.make_output = lambda: {
            'pt_leading_lepton':        self.create_hist('pt_leadlep',        'process', 'region', (200,   0, 2000), r'$p_{T}$ of the leading lepton [GeV]'),
            'eta_leading_lepton':       self.create_hist('eta_leadlep',       'process', 'region', (60,   -3,    3), r'$\eta$ of the leading lepton'),
            'phi_leading_lepton':       self.create_hist('phi_leadlep',       'process', 'region', (80,   -4,    4), r'$\phi$ of the leading lepton'),

            'pt_subleading_lepton':     self.create_hist('pt_subleadlep',     'process', 'region', (200,   0, 2000), r'$p_{T}$ of the subleading lepton [GeV]'),
            'eta_subleading_lepton':    self.create_hist('eta_subleadlep',    'process', 'region', (60,   -3,    3), r'$\eta$ of the subleading lepton'),
            'phi_subleading_lepton':    self.create_hist('phi_subleadlep',    'process', 'region', (80,   -4,    4), r'$\phi$ of the subleading lepton'),

            'pt_leading_jet':           self.create_hist('pt_leadjet',           'process', 'region', (200,   0, 2000), r'$p_{T}$ of the leading jet [GeV]'),
            'eta_leading_jet':          self.create_hist('eta_leadjet',          'process', 'region', (60,   -3,    3), r'$\eta$ of the leading jet'),
            'phi_leading_jet':          self.create_hist('phi_leadjet',          'process', 'region', (80,   -4,    4), r'$\phi$ of the leading jet'),

            'pt_subleading_jet':        self.create_hist('pt_subleadjet',        'process', 'region', (200,   0, 2000), r'$p_{T}$ of the subleading jet [GeV]'),
            'eta_subleading_jet':       self.create_hist('eta_subleadjet',       'process', 'region', (60,   -3,    3), r'$\eta$ of the subleading jet'),
            'phi_subleading_jet':       self.create_hist('phi_subleadjet',       'process', 'region', (80,   -4,    4), r'$\phi$ of the subleading jet'),

            'mass_dilepton':            self.create_hist('mass_dilepton',            'process', 'region', (5000,  0, 5000), r'$m_{\ell\ell}$ [GeV]'),
            'pt_dilepton':              self.create_hist('pt_dilepton',              'process', 'region', (200,   0, 2000), r'$p_{T,\ell\ell}$ [GeV]'),
 
            'mass_dijet':               self.create_hist('mass_dijet',               'process', 'region', (500,   0, 5000), r'$m_{jj}$ [GeV]'),
            'pt_dijet':                 self.create_hist('pt_dijet',                 'process', 'region', (500,   0, 5000), r'$p_{T,jj}$ [GeV]'),

            'mass_threeobject_leadlep':  self.create_hist('mass_threeobject_leadlep',  'process', 'region', (800,   0, 8000), r'$m_{\ell jj}$ [GeV]'),
            'pt_threeobject_leadlep':    self.create_hist('pt_threeobject_leadlep',    'process', 'region', (800,   0, 8000), r'$p_{T,\ell jj}$ [GeV]'),

            'mass_threeobject_subleadlep': self.create_hist('mass_threeobject_subleadlep', 'process', 'region', (800,   0, 8000), r'$m_{\ell jj}$ [GeV]'),
            'pt_threeobject_subleadlep':   self.create_hist('pt_threeobject_subleadlep',   'process', 'region', (800,   0, 8000), r'$p_{T,\ell jj}$ [GeV]'),

            'mass_fourobject':        self.create_hist('mass_fourobject',        'process', 'region', (800,   0, 8000), r'$m_{\ell\ell jj}$ [GeV]'),
            'pt_fourobject':          self.create_hist('pt_fourobject',          'process', 'region', (800,   0, 8000), r'$p_{T,\ell\ell jj}$ [GeV]'),

            ##adding histograms for boosted region
            'pt_leading_loose_lepton':        self.create_hist('pt_leadlooselep',        'process', 'region', (200,   0, 2000), r'$p_{T}$ of the leading loose lepton [GeV]'),
            'eta_leading_loose_lepton':       self.create_hist('eta_leadlooselep',       'process', 'region', (60,   -3,    3), r'$\eta$ of the leading loose lepton'),
            'phi_leading_loose_lepton':       self.create_hist('phi_leadlooselep',       'process', 'region', (80,   -4,    4), r'$\phi$ of the leading loose lepton'),
             'pt_leading_AK8Jets':        self.create_hist('pt_leadAK8Jets',        'process', 'region', (200,   0, 2000), r'$p_{T}$ of the leading  AK8Jets [GeV]'),
            'eta_leading_AK8Jets':       self.create_hist('eta_leadAK8Jets',       'process', 'region', (60,   -3,    3), r'$\eta$ of theleading  AK8Jets'),
            'phi_leading_AK8Jets':       self.create_hist('phi_leadAK8Jets',       'process', 'region', (80,   -4,    4), r'$\phi$ of theleading  AK8Jets'),
            'LSF_leading_AK8Jets':        self.create_hist('LSF_leadingAK8Jets',        'process', 'region', (200,   0, 1.1), r'LSF of leading AK8Jets'),
            'mass_twoobject':        self.create_hist('mass_twoobject',        'process', 'region', (800,   0, 8000), r'$m_{\ell\ell jj}$ [GeV]'),
            'pt_twoobject':          self.create_hist('pt_twoobject',          'process', 'region', (800,   0, 8000), r'$p_{T,\ell\ell jj}$ [GeV]'),
            'count' : self.create_hist('count','process', 'region', (100,0,100), r'count'),
            'dPhi_leading_tightlepton_AK8Jet':       self.create_hist('dPhi_leadTightlep_AK8Jets',       'process', 'region', (80,   -4,    4), r'$d\phi$ (leading Tight lepton, AK8 Jet)'),

            'nAK8Jets' : self.create_hist('nAK8Jets','process','region',(10,0,10),r'nAK8Jets'),
            'nAK4Jets' : self.create_hist('nAK4Jets','process','region',(10,0,10),r'nAK4Jets'),
            'ntightLeptons' : self.create_hist('ntightLeptons','process','region',(10,0,10),r'ntightLeptons'),
            'nlooseLeptons' : self.create_hist('nlooseLeptons','process','region',(10,0,10),r'nlooseLeptons'),
            'ntightElectrons' : self.create_hist('ntightElectrons','process','region',(10,0,10),r'ntightElectrons'),
            'nlooseElectrons' : self.create_hist('nlooseElectrons','process','region',(10,0,10),r'nlooseElectrons'),
            'ntightMuons' : self.create_hist('ntightMuons','process','region',(10,0,10),r'ntightMuons'),
            'nlooseMuons' : self.create_hist('nlooseMuons','process','region',(10,0,10),r'nlooseMuons'),
            
            ## define 2D histogram to debug ---
            'nAK8vsnAK4' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','nAK4',(10,0,10),r'n AK4 Jets'),
            'nAK8vsntightLeptons' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','ntightLeptons',(10,0,10),r'ntight Leptons'),
            'nAK8vsnlooseLeptons' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','nlooseLeptons',(10,0,10),r'nloose Leptons'),
            'nAK8vsntightElectrons' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','ntightElectrons',(10,0,10),r'ntight Electrons'),
            'nAK8vsnlooseElectrons' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','nlooseElectrons',(10,0,10),r'nloose Electrons'),
            'nAK8vsntightMuons' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','ntightMuons',(10,0,10),r'ntight Muons'),
            'nAK8vsnlooseMuons' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','nlooseMuons',(10,0,10),r'nloose Muons'),

            'nAK4vsntightLeptons' : self.create_hist2D('nAK4', 'process','region',(10,0,10),r'n AK4 Jets','ntightLeptons',(10,0,10),r'ntight Leptons'),
            'nAK4vsnlooseLeptons' : self.create_hist2D('nAK4', 'process','region',(10,0,10),r'n AK4 Jets','nlooseLeptons',(10,0,10),r'nloose Leptons'),
            'nAK4vsntightElectrons' : self.create_hist2D('nAK4', 'process','region',(10,0,10),r'n AK4 Jets','ntightElectrons',(10,0,10),r'ntight Electrons'),
            'nAK4vsnlooseElectrons' : self.create_hist2D('nAK4', 'process','region',(10,0,10),r'n AK4 Jets','nlooseElectrons',(10,0,10),r'nloose Electrons'),
            'nAK4vsntightMuons' : self.create_hist2D('nAK4', 'process','region',(10,0,10),r'n AK4 Jets','ntightMuons',(10,0,10),r'ntight Muons'),
            'nAK4vsnlooseMuons' : self.create_hist2D('nAK4', 'process','region',(10,0,10),r'n AK4 Jets','nlooseMuons',(10,0,10),r'nloose Muons'),


            'nloosevsntightLeptons' : self.create_hist2D('nlooseLeptons', 'process','region',(10,0,10),r'n loose Leptons','ntightLeptons',(10,0,10),r'ntight Leptons'),
            'nAK8vsmlj' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','mlj',(800,0,8000),r'mlj'),
            'nAK8vsmll' : self.create_hist2D('nAK8', 'process','region',(10,0,10),r'n AK8 Jets','mll',(800,0,8000),r'mll'),
            'mllvsmlj' : self.create_hist2D('mll', 'process','region',(800,0,8000),r'mll','mlj',(800,0,8000),r'mlj'),

        }

        # ——— Load SF lookup if provided ———
        if sf_file:
            fname = os.path.basename(sf_file)
            self.variable = fname.replace("_sf.json", "")
            with open(sf_file) as jf:
                data = json.load(jf)
            edges = np.array(data["edges"], dtype=float)
            sf_EE = np.array(data["sf_ee_resolved_dy_cr"], dtype=float)
            sf_MM = np.array(data["sf_mumu_resolved_dy_cr"], dtype=float)

            self.lookup_EE = dense_lookup(sf_EE, [edges])
            self.lookup_MM = dense_lookup(sf_MM, [edges])
            logger.info(f"Loaded {self.variable} SF lookup from {sf_file}")
        else:
            self.variable = None
            self.lookup_EE = None
            self.lookup_MM = None

    def create_hist(self, name, process, region, bins, label):
        """Helper function to create histograms."""
        return (
            hist.Hist.new.StrCat([], name="process", label="Process", growth=True)
            .StrCat([], name="region", label="Analysis Region", growth=True)
            .Reg(*bins, name=name, label=label)
            .Weight()
        )
    def create_hist2D(self, name_x, process, region, bins_x, label_x, name_y, bins_y, label_y):
        """Helper function to create 2D histograms with process & region axes."""
        return (
            hist.Hist.new.StrCat([], name="process", label="Process", growth=True)
            .StrCat([], name="region", label="Analysis Region", growth=True)
            .Reg(*bins_x, name=name_x, label=label_x)
            .Reg(*bins_y, name=name_y, label=label_y)
            .Weight()
        )

    def selectElectrons(self, events):
        tight_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.cutBased_HEEP)
        loose_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.isLoose) #cutBased == 2)
        return events.Electron[tight_electrons], events.Electron[loose_electrons]

    def selectMuons(self, events):
        tight_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2) & (events.Muon.tkRelIso < 0.1)
        loose_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2)
        return events.Muon[tight_muons], events.Muon[loose_muons]

    def selectJets(self, events):
        ak4_jets = (events.Jet.pt > 40) & (np.abs(events.Jet.eta) < 2.4) & (events.Jet.isTightLeptonVeto)
        return events.Jet[ak4_jets]

    def selectAK8Jets(self,events):
        ak8_jets = (events.FatJet.pt > 200) & (np.abs(events.FatJet.eta) < 2.4)  & (events.FatJet.msoftdrop > 40) & (events.FatJet.isTight) 
        return events.FatJet[ak8_jets]
    
    def check_mass_point_resolved(self):
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
        selections.add("minTwoAK4Jets", (ak.num(AK4Jets) >= 2) ) #& (AK4Jets[:,0].pt !=0) & (AK4Jets[:,1].pt !=0))
        selections.add("leadTightLeptonPt60", (ak.any(tightElectrons.pt > 60, axis=1) | ak.any(tightMuons.pt > 60, axis=1)))
        selections.add("mlljj>800", mlljj > 800)
        selections.add("dr>0.4", (dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

    def add_boosted_selections(self, selections, tightElectrons, tightMuons, AK4Jets, AK8Jets, looseElectrons, looseMuons,dr_jl_min, dr_j1j2, dr_l1l2):
        # selections.add("nottwoTightLeptons", (ak.num(tightElectrons) + ak.num(tightMuons)) == 1)
        # selections.add("notminTwoAK4Jets", ak.num(AK4Jets) <=1)
        selections.add("atleast1AK8Jets", (AK8Jets >=1))
        selections.add("atleast1LooseLepton",(ak.num(looseElectrons) + ak.num(looseMuons))>=1)
        #selections.add("notdr>0.4", ~((dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4)))
        resolved = ((ak.num(tightElectrons) + ak.num(tightMuons)) == 2) & ((ak.num(AK4Jets) >= 2)) & ((dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

        selections.add("notResolved", ~resolved)

        #selections.add("notResolved",~(selections.all("twoTightLeptons") & selections.all("minTwoAK4Jets") & selections.all("dr>0.4")))
        # (selections.all("nottwoTightLeptons") | selections.all("notminTwoAK4Jets") ))#| selections.all("notdr>0.4")) )#~(selections.all("twoTightLeptons") & selections.all("minTwoAK4Jets") & selections.all("dr>0.4")))

    def fill_basic_histograms(self, output, region, cut, process_name, jets, leptons, ak8jets, looseleptons, leptons_all,mll_boosted,nLeptons,nElectrons, nMuons, nLooseLeptons, nLooseElectrons, nLooseMuons, nAK8Jets, nAK4Jets, weights):
        variables =[
            ('pt_leading_lepton',         leptons[:, 0].pt,    'pt_leadlep'),
            ('eta_leading_lepton',        leptons[:, 0].eta,   'eta_leadlep'),
            ('phi_leading_lepton',        leptons[:, 0].phi,   'phi_leadlep'),

            ]
        if "resolved" in region:            
            variables = [
                ('pt_leading_lepton',         leptons[:, 0].pt,    'pt_leadlep'),
                ('eta_leading_lepton',        leptons[:, 0].eta,   'eta_leadlep'),
                ('phi_leading_lepton',        leptons[:, 0].phi,   'phi_leadlep'),
                ('pt_subleading_lepton',      leptons[:, 1].pt,    'pt_subleadlep'),
                ('eta_subleading_lepton',     leptons[:, 1].eta,   'eta_subleadlep'),
                ('phi_subleading_lepton',     leptons[:, 1].phi,   'phi_subleadlep'),
                ('pt_leading_jet',            jets[:, 0].pt,       'pt_leadjet'),
                ('eta_leading_jet',           jets[:, 0].eta,      'eta_leadjet'),
                ('phi_leading_jet',           jets[:, 0].phi,      'phi_leadjet'),
                ('pt_subleading_jet',         jets[:, 1].pt,       'pt_subleadjet'),
                ('eta_subleading_jet',        jets[:, 1].eta,      'eta_subleadjet'),
                ('phi_subleading_jet',        jets[:, 1].phi,      'phi_subleadjet'),
                ('mass_dilepton',             (leptons[:, 0] + leptons[:, 1]).mass, 'mass_dilepton'),
                ('pt_dilepton',               (leptons[:, 0] + leptons[:, 1]).pt,   'pt_dilepton'),
                ('mass_dijet',                (jets[:, 0] + jets[:, 1]).mass,       'mass_dijet'),
                ('pt_dijet',                  (jets[:, 0] + jets[:, 1]).pt,         'pt_dijet'),
                ('mass_threeobject_leadlep',  (leptons[:, 0] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_leadlep'),
                ('pt_threeobject_leadlep',    (leptons[:, 0] + jets[:, 0] + jets[:, 1]).pt,   'pt_threeobject_leadlep'),
                ('mass_threeobject_subleadlep', (leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_threeobject_subleadlep'),
                ('pt_threeobject_subleadlep',  (leptons[:, 1] + jets[:, 0] + jets[:, 1]).pt,   'pt_threeobject_subleadlep'),
                ('mass_fourobject',           (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass, 'mass_fourobject'),
                ('pt_fourobject',             (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).pt,   'pt_fourobject'),
            ]
        elif "check_region" in region :
            #print("im in check region")
            variables =[
                ('count',         leptons_all,    'count'),
                ('nAK8Jets',nAK8Jets,'nAK8Jets'),
                ('nAK4Jets',nAK4Jets,'nAK4Jets'),
                ('ntightLeptons',nLeptons,'ntightLeptons'),
                ('nAK8vsnAK4', nAK8Jets, nAK4Jets,'nAK8vsnAK4'),
                ]
            variables_1D = [
                ('count', leptons_all, 'count'),
                ('nAK8Jets', nAK8Jets, 'nAK8Jets'),
                ('nAK4Jets', nAK4Jets, 'nAK4Jets'),
                ('ntightLeptons', nLeptons, 'ntightLeptons'),
                ('nlooseLeptons', nLooseLeptons, 'nlooseLeptons'),
                ('nlooseElectrons', nLooseElectrons, 'nlooseElectrons'),
                ('nlooseMuons', nLooseMuons, 'nlooseMuons'),
                ('ntightElectrons', nElectrons, 'ntightElectrons'),
                ('ntightMuons', nMuons, 'ntightMuons'),

            ]

            # 2D histograms
            variables_2D = [
                ('nAK8vsnAK4', (nAK8Jets, nAK4Jets), ('nAK8', 'nAK4')),
                ('nAK8vsntightLeptons', (nAK8Jets, nLeptons), ('nAK8', 'ntightLeptons')),
                ('nAK8vsnlooseLeptons', (nAK8Jets, nLooseLeptons), ('nAK8', 'nlooseLeptons')),
                ('nAK8vsntightElectrons', (nAK8Jets, nElectrons), ('nAK8', 'ntightElectrons')),
                ('nAK8vsnlooseElectrons', (nAK8Jets, nLooseElectrons), ('nAK8', 'nlooseElectrons')),
                ('nAK8vsntightMuons', (nAK8Jets, nMuons), ('nAK8', 'ntightMuons')),
                ('nAK8vsnlooseMuons', (nAK8Jets, nLooseMuons), ('nAK8', 'nlooseMuons')),
                ('nAK4vsntightLeptons', (nAK4Jets, nLeptons), ('nAK4', 'ntightLeptons')),
                ('nAK4vsnlooseLeptons', (nAK4Jets, nLooseLeptons), ('nAK4', 'nlooseLeptons')),
                ('nAK4vsntightElectrons', (nAK4Jets, nElectrons), ('nAK4', 'ntightElectrons')),
                ('nAK4vsnlooseElectrons', (nAK4Jets, nLooseElectrons), ('nAK4', 'nlooseElectrons')),
                ('nAK4vsntightMuons', (nAK4Jets, nMuons), ('nAK4', 'ntightMuons')),
                ('nAK4vsnlooseMuons', (nAK4Jets, nLooseMuons), ('nAK4', 'nlooseMuons')),

                ('nloosevsntightLeptons', (nLooseLeptons, nLeptons), ('nlooseLeptons', 'ntightLeptons')),
                ]


            
            # if 'v1' in region :
            #      variables_2D = [
            #          ('nAK8vsmlj', (nAK8Jets, (leptons[:, 0] + ak8jets[:, 0] ).mass), ('nAK8', 'mlj')),
            #          ('nAK8vsmll', (nAK8Jets, (leptons[:, 0] + looseleptons[:, 0]).mass), ('nAK8', 'mll')),

            #          ('mllvsmlj', ((leptons[:, 0] + looseleptons[:, 0]).mass, (leptons[:, 0] + ak8jets[:, 0] ).mass), ('mll', 'mlj')),
            # ]
            
            variables = variables_1D + variables_2D
        else:
            variables = [
                ('pt_leading_lepton',         leptons[:, 0].pt,    'pt_leadlep'),
                ('eta_leading_lepton',        leptons[:, 0].eta,   'eta_leadlep'),
                ('phi_leading_lepton',        leptons[:, 0].phi,   'phi_leadlep'),
                ('pt_leading_loose_lepton',      looseleptons[:, 0].pt,    'pt_leadlooselep'),
                ('eta_leading_loose_lepton',     looseleptons[:, 0].eta,   'eta_leadlooselep'),
                ('phi_leading_loose_lepton',     looseleptons[:, 0].phi,   'phi_leadlooselep'),
                ('pt_leading_AK8Jets',            ak8jets[:, 0].pt,       'pt_leadAK8Jets'),
                ('eta_leading_AK8Jets',           ak8jets[:, 0].eta,      'eta_leadAK8Jets'),
                ('phi_leading_AK8Jets',           ak8jets[:, 0].phi,      'phi_leadAK8Jets'),
                ('mass_dilepton',             mll_boosted, 'mass_dilepton'),
                ('pt_dilepton',               (leptons[:, 0] + looseleptons[:, 0]).pt,   'pt_dilepton'),
                ('mass_twoobject',           (leptons[:, 0] + ak8jets[:, 0] ).mass, 'mass_twoobject'),
                ('pt_twoobject',             (leptons[:, 0] + ak8jets[:, 0]).pt,   'pt_twoobject'),
                ('LSF_leading_AK8Jets', ak8jets[:,0].lsf3,'LSF_leadingAK8Jets'),
                ('dPhi_leading_tightlepton_AK8Jet',  ak8jets[:, 0].delta_phi(leptons[:,0]),'dPhi_leadTightlep_AK8Jets')
            ]

        if self.variable is not None:
            for _, vals_array, axis_name in variables:
                if axis_name == self.variable:
                    vals_all = vals_array
                    break

        # for hist_name, values, axis_name in variables:
        #     vals = values[cut]
        #     w = weights.weight()[cut]

        #     if process_name == "DYJets" and self.lookup_EE is not None:
        #         if region.startswith("wr_ee_resolved_dy_cr") or region.startswith("wr_ee_resolved_sr"):
        #             corr = self.lookup_EE(vals_all[cut])
        #         elif region.startswith("wr_mumu_resolved_dy_cr") or region.startswith("wr_mumu_resolved_sr"):
        #             corr = self.lookup_MM(vals_all[cut])
        #         else:
        #             corr = 1.0
        #         w = w * corr

        #     output[hist_name].fill(
        #         process=process_name,
        #         region=region,
        #         **{axis_name: vals},
        #         weight=w
        #     )
        for var in variables:
            hist_name = var[0]
            vals = var[1]
            axis_name = var[2]
            
            w = weights.weight()[cut]
            
            # Apply DY corrections if needed
            if process_name == "DYJets" and self.lookup_EE is not None:
                if region.startswith("wr_ee_resolved_dy_cr") or region.startswith("wr_ee_resolved_sr"):
                    corr = self.lookup_EE(vals[cut] if isinstance(vals, ak.Array) else vals[0][cut])
                elif region.startswith("wr_mumu_resolved_dy_cr") or region.startswith("wr_mumu_resolved_sr"):
                    corr = self.lookup_MM(vals[cut] if isinstance(vals, ak.Array) else vals[0][cut])
                else:
                    corr = 1.0
                w = w * corr
                    
            # Fill 1D or 2D
            if isinstance(vals, tuple):  # 2D histogram
                output[hist_name].fill(
                    process=process_name,
                    region=region,
                    **{axis_name[0]: vals[0][cut], axis_name[1]: vals[1][cut]},
                    weight=w
                )
            else:  # 1D histogram
                output[hist_name].fill(
                    process=process_name,
                    region=region,
                    **{axis_name: vals[cut]},
                    weight=w
                )


            
    def process(self, events):
        output = self.make_output()
        metadata = events.metadata

        mc_campaign = metadata.get("era", "")
        process_name = metadata.get("physics_group", "")
        dataset = metadata.get("sample", "")
        isRealData = not hasattr(events, "genWeight")

#        logger.info(f"\n\nAnalyzing {len(events)} {dataset} events.\n\n")

        if isRealData:
            if mc_campaign == "RunIISummer20UL18":
                lumi_mask = LumiMask("data/lumis/RunII/2018/RunIISummer20UL18/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt")
            elif mc_campaign in ("Run3Summer22", "Run3Summer22EE"):
                lumi_mask = LumiMask("data/lumis/Run3/2022/Run3Summer22/Cert_Collisions2022_355100_362760_Golden.txt")
            events = events[lumi_mask(events.run, events.luminosityBlock)]

        # if process_name == "Signal":
        #     self.check_mass_point_resolved()

        ## preobject selection
        # leptons = ak.with_name(ak.concatenate((events.Electron, events.Muon), axis=1), 'PtEtaPhiMCandidate')
        # sorted_indices = ak.argsort(leptons.pt, axis=1, ascending=False)
        # leptons = leptons[sorted_indices]
        # leptons_padded = ak.pad_none(leptons, 2, clip=True)
        # leading_lepton = leptons_padded[:, 0]
        # subleading_lepton = leptons_padded[:, 1]
        # #nleptons = ak.fill_none(ak.sum(leptons_padded), 0)
        # lead_pt_cut = 52 #5
        # sublead_pt_cut = 45 #5

        # Object selection
        # tightElectrons, looseElectrons = self.selectElectrons(events) 
        # nTightElectrons =ak.fill_none(ak.num(tightElectrons),0)

        # nLooseElectrons = ak.num(looseElectrons)
        # tightMuons, looseMuons = self.selectMuons(events)
        # nTightMuons = ak.fill_none(ak.num(tightMuons),0)
        # nLooseMuons = ak.num(looseMuons)
        # nLeptons = nTightElectrons + nTightMuons
        # nLooseLeptons = nLooseMuons +nLooseElectrons
        # AK4Jets = self.selectJets(events)
        # nAK4Jets = ak.fill_none(ak.num(AK4Jets),0)
        
        # AK8Jets = self.selectAK8Jets(events) 
        # nAK8Jets = ak.num(AK8Jets)

        tightElectrons, looseElectrons = self.selectElectrons(events)
        nTightElectrons = ak.fill_none(ak.num(tightElectrons), 0)
        nLooseElectrons = ak.fill_none(ak.num(looseElectrons), 0)

        tightMuons, looseMuons = self.selectMuons(events)
        nTightMuons = ak.fill_none(ak.num(tightMuons), 0)
        nLooseMuons = ak.fill_none(ak.num(looseMuons), 0)

        nLeptons       = nTightElectrons + nTightMuons
        nLooseLeptons  = nLooseMuons + nLooseElectrons

        AK4Jets = self.selectJets(events)
        nAK4Jets = ak.fill_none(ak.num(AK4Jets), 0)

        AK8Jets = self.selectAK8Jets(events)
        nAK8Jets = ak.fill_none(ak.num(AK8Jets), 0)

        # Event variables
        tightLeptons_all = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        
        tightLeptons_all = tightLeptons_all[ak.argsort(tightLeptons_all.pt, axis=1, ascending=False)] #,1 , axis=1)
        tightLeptons = ak.pad_none(tightLeptons_all, 2, axis=1)
        AK4Jets = AK4Jets[ak.argsort(AK4Jets.pt, axis=1, ascending=False)]
        AK4Jets_notpadded = AK4Jets # quick fix
        AK4Jets = ak.pad_none(AK4Jets, 2, axis=1)
        
        
        mjj = ak.fill_none((AK4Jets[:, 0] + AK4Jets[:, 1]).mass, False)
        
        mll = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1]).mass, False)

        mlljj = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1] + AK4Jets[:, 0] + AK4Jets[:, 1]).mass, False)

        dr_jl_min = ak.fill_none(ak.min(AK4Jets[:, :2].nearest(tightLeptons).delta_r(AK4Jets[:, :2]), axis=1), False)
        dr_j1j2 = ak.fill_none(AK4Jets[:, 0].delta_r(AK4Jets[:, 1]), False)
        dr_l1l2 = ak.fill_none(tightLeptons[:, 0].delta_r(tightLeptons[:, 1]), False)

        AK8Jets = AK8Jets[ak.argsort(AK8Jets.pt, axis=1, ascending=False)]
        AK8Jets = ak.pad_none(AK8Jets, 1, axis=1) 
        dPhi_lj = ak.fill_none(AK8Jets[:, 0].delta_phi(tightLeptons[:,0]),0) 
        # ## adding for loose leptons                                                                                                          
        looseLeptons_all = ak.with_name(ak.concatenate((looseElectrons, looseMuons), axis=1), 'PtEtaPhiMCandidate')
        looseLeptons_all = looseLeptons_all[ak.argsort(looseLeptons_all.pt, axis=1, ascending=False)] #, 1, axis=1)
        looseLeptons = ak.pad_none(looseLeptons_all, 1, axis=1)
        # All combinations of tight and loose leptons
        # shape: [events, n_tight, n_loose]
        # mll_all = (tightLeptons[:, :, None] + looseLeptons[:, None, :]).mass
        
        # # Flatten the last two axes to make 1D per event
        # mll_flat = ak.flatten(mll_all, axis=1)
        
        # # Take maximum mass per event
        # #mll_boosted = ak.max(mll_flat, axis=1)  # axis=1 is now fine
        # mll_boosted = ak.fill_none(ak.max(mll_flat, axis=1, mask_identity=True), 0.0)
        # mlj_all = (tightLeptons[:, :, None] + AK8Jets[:, None, :]).mass
        # mlj_flat = ak.flatten(mlj_all, axis=1)
        # #mlj_boosted = ak.max(mlj_flat, axis=1)
        # mlj_boosted = ak.fill_none(ak.max(mlj_flat, axis=1, mask_identity=True), 0.0)
        # # All combinations
        # mll_all = (tightLeptons[:, :, None] + looseLeptons[:, None, :]).mass
        # mll_flat = ak.flatten(mll_all, axis=1)
        # # Maximum per event
        # mll_boosted = ak.max(mll_flat, axis=(1,2))

        # #mll_boosted =ak.fill_none((tightLeptons[:, 0] + looseLeptons[:, 0]).mass, 0.0)
        # mlj_all = (tightLeptons[:, :, None] + AK8Jets[:, None, :]).mass
        # mlj_flat = ak.flatten(mlj_all, axis=1)
        # mlj_boosted = ak.max(mlj_flat, axis=(1,2))
        mll_boosted =ak.fill_none((tightLeptons[:, 0] + looseLeptons[:, 0]).mass, 0.0)
        mlj_boosted =ak.fill_none((tightLeptons[:, 0] +AK8Jets[:,0]).mass, 0.0)
        dR_ak8j_looselepton = ak.fill_none(ak.min(AK8Jets[:, 0:1].nearest(looseLeptons).delta_r(AK8Jets[:, 0:1]), axis=1), False)#ak.fill_none(AK8Jets[:, 0:1].delta_r(looseLeptons[:,0:1]), 999 ) #AK8Jets[:, 0:1].nearest(looseLeptons).delta_r(AK8Jets[:, 0:1]), 999 )
        #ak.fill_none(ak.min(AK8Jets[:, 0:1].nearest(looseLeptons).delta_r(AK8Jets[:, 0:1]), axis=1), False)


        # Event selections
        selections = PackedSelection()
        self.add_resolved_selections(selections, tightElectrons, tightMuons, AK4Jets, mlljj, dr_jl_min, dr_j1j2, dr_l1l2)
        self.add_boosted_selections(selections, tightElectrons, tightMuons, AK4Jets_notpadded,nAK8Jets, looseElectrons, looseMuons,dr_jl_min, dr_j1j2, dr_l1l2)
        # Trigger selections
        if mc_campaign in ("RunIISummer20UL18", "Run2Autumn18"): 
            eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
            muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100
            selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
            selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
            selections.add("emuTrigger", (eTrig & muTrig & (nTightElectrons == 1) & (nTightMuons == 1)))
            # selections.add("eeTrigger_boosted",(eTrig & (nTightElectrons == 1) & (nTightMuons == 0)))# & (nLooseElectrons >= 1 ) & (nLooseMuons==0)))
            # selections.add("mumuTrigger_boosted",(muTrig & (nTightElectrons == 0)  & (nTightMuons == 1 ) & (nLooseMuons >= 1) & (nLooseElectrons == 0 )))
            # selections.add("emuTrigger_boosted",(eTrig  & (nTightElectrons == 1) & (nTightMuons == 0) & (nLooseMuons >= 1) & (nLooseElectrons == 0 ) & (dR_ak8j_looselepton < 0.8)))## add dR condition between loose and AK8 jets - come back to it again for 0.8 or 0.4 clarification
            # selections.add("mueTrigger_boosted",( muTrig & (nTightMuons == 1) & (nTightElectrons == 0) & (nLooseElectrons >= 1 ) & (nLooseMuons==0) & (dR_ak8j_looselepton < 0.8)))
            
        elif mc_campaign in ("Run3Summer22", "Run3Summer23BPix", "Run3Summer22EE", "Run3Summer23"):
            eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
            muTrig = events.HLT.Mu50 | events.HLT.HighPtTkMu100
            selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
            selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
            selections.add("emuTrigger", ((eTrig | muTrig) & (nTightElectrons == 1) & (nTightMuons == 1)))
            # selections.add("eeTrigger_boosted",(eTrig & (nTightElectrons == 1 ) & (nTightMuons == 0)))# & (nLooseElectrons >= 1 ) & (nLooseMuons==0) ))
            # selections.add("mumuTrigger_boosted",(muTrig & (nTightElectrons == 0)  & (nTightMuons == 1) & (dR_ak8j_looselepton < 0.8) & (nLooseMuons >= 1) & (nLooseElectrons == 0 ) ))
            # selections.add("emuTrigger_boosted",(eTrig & (nTightElectrons == 1) & (nTightMuons == 0) & (nLooseMuons >= 1) & (nLooseElectrons == 0 ) & (dR_ak8j_looselepton < 0.8) ))                                                      
            # selections.add("mueTrigger_boosted",(muTrig & (nTightMuons == 1) & (nTightElectrons == 0) & (nLooseElectrons >= 1) & (nLooseMuons==0) & (dR_ak8j_looselepton < 0.8 )))

        #selections.add("skim_select",(leading_lepton.pt > lead_pt_cut) & (subleading_lepton.pt > sublead_pt_cut))

        # Event Weights
        weights = Weights(len(events))
        if not (not hasattr(events, "genWeight")):  # is MC
            eventWeight = abs(np.sign(events.event))
            if mc_campaign == "RunIISummer20UL18" and process_name == "DYJets":
                eventWeight = eventWeight * 1.35

            if process_name != "Signal":
                sf = metadata['xsec'] / metadata['nevts']
                eventWeight = eventWeight * sf * 59.83 * 1000
            else:
                sf = metadata['xsec'] / metadata['nevts']
                eventWeight = eventWeight * sf
        else:
            eventWeight = abs(np.sign(events.event))

        
        weights.add("event_weight", weight=eventWeight)

        selections.add("eejj", ((ak.num(tightElectrons) == 2) & (ak.num(tightMuons) == 0)))
        selections.add("mumujj", ((ak.num(tightElectrons) == 0) & (ak.num(tightMuons) == 2)))
        selections.add("emujj", ((ak.num(tightElectrons) == 1) & (ak.num(tightMuons) == 1)))
        selections.add("ej", (nTightElectrons==1) & (nTightMuons==0))#((ak.num(tightElectrons) == 1) & (ak.num(tightMuons) == 0)))# & (ak.num(looseElectrons) >= 1) & (ak.num(looseMuons) == 0))
        selections.add("muj", (nTightElectrons==0) & (nTightMuons==1))#((ak.num(tightElectrons) == 0) & (ak.num(tightMuons) == 1)) & (ak.num(looseElectrons) == 0) & (ak.num(looseMuons) >= 1))
        selections.add("emuj", (nTightElectrons == 1) & (nTightMuons == 0) & (nLooseElectrons == 0) & (nLooseMuons >= 1))
        selections.add("muej", (nTightElectrons == 0) & (nTightMuons == 1) & (nLooseElectrons >= 1) & (nLooseMuons ==0))
        #        selections.add("muej", ((ak.num(tightElectrons) == 0) & (ak.num(tightMuons) == 1)) & (ak.num(looseElectrons) >= 1) & (ak.num(looseMuons) ==0))
        
        
        # mll selections
        selections.add("60mll150", ((mll > 60) & (mll < 150)))
        selections.add("400mll", (mll > 400))


        selections.add("60mll_boosted150",((mll_boosted>60) & (mll_boosted<150)))
        selections.add("200mll_boosted",(mll_boosted>200))
        selections.add("mlj>800",(mlj_boosted>800))
        selections.add("AK8Jets_LSF3>0.75",(AK8Jets[:,0].lsf3 > 0.75))
        selections.add("dPhi_lj>2.0",(dPhi_lj>2.0) | (dPhi_lj <-2.0))
        selections.add("atleast1tightLepton",(nLeptons>=0))
        #(nTighteptonsElectrons==1) & (nTightMuons==0))  | ((nTightElectrons==0) & (nTightMuons==1)))
        # Define regions
        regions = {
            'wr_ee_resolved_dy_cr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger' , 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
            'wr_mumu_resolved_dy_cr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
            'wr_resolved_flavor_cr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
            'wr_ee_resolved_sr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'wr_mumu_resolved_sr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],

            'wr_ee_boosted_sr' :['atleast1AK8Jets','leadTightLeptonPt60','atleast1LooseLepton'],#,'dPhi_lj>2.0'], #,'eeTrigger_boosted'], # '200mll_boosted','mlj>800','atleast1LooseLepton','eeTrigger_boosted','dPhi_lj>2.0'],
#             # ['nottwoTightLeptons','atleast1AK8Jets','leadTightLeptonPt60', '200mll_boosted','mlj>800','atleast1LooseLepton','notminTwoAK4Jets','notdr>0.4','eeTrigger_boosted','dPhi_lj>2.0'], #'AK8Jets_LSF3>0.75','dPhi_lj>2.0'],
#             'wr_ee_boosted_dy_cr' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton'],#,'60mll_boosted150','mlj>800','ej'],#'dPhi_lj>2.0'],
#             'wr_ee_boosted_dy_cr_mll' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton', '60mll_boosted150'],
#             'wr_ee_boosted_dy_cr_mlj' :	['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton', '60mll_boosted150','mlj>800'],
#             'wr_ee_boosted_dy_cr_ee' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton', '60mll_boosted150','mlj>800','ej'],
#             'wr_ee_boosted_dy_cr_mumu' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton', '60mll_boosted150','mlj>800','muj'],
#             'wr_ee_boosted_dy_cr_emu' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton', '60mll_boosted150','mlj>800','emuj'],

#             #'60mll_boosted150','mlj>800','atleast1LooseLepton','eeTrigger_boosted','dPhi_lj>2.0'],
# #['nottwoTightLeptons','atleast1AK8Jets','leadTightLeptonPt60', '60mll_boosted150','mlj>800','atleast1LooseLepton','notminTwoAK4Jets','notdr>0.4','eeTrigger_boosted','dPhi_lj>2.0'] , #,'AK8Jets_LSF3>0.75'],
#             'wr_boosted_flavor_emu_cr' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton', '200mll_boosted','mlj>800','emuj'],#,'dPhi_lj>2.0'], #'AK8Jets_LSF3>0.75', 'dPhi_lj>2.0','emuTrigger_boosted'],
#             'wr_boosted_flavor_mue_cr' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60','atleast1LooseLepton','200mll_boosted','mlj>800','muej'],#Trigger_boosted', 'dPhi_lj>2.0'],#'AK8Jets_LSF3>0.75', 'dPhi_lj>2.0','mueTrigger_boosted'],
#             'wr_mumu_boosted_sr' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60', 'atleast1LooseLepton','200mll_boosted','mlj>800','muj'],# 'dPhi_lj>2.0'],#'AK8Jets_LSF3>0.75','dPhi_lj>2.0'],
#             'wr_mumu_boosted_dy_cr' : ['notResolved','atleast1AK8Jets','leadTightLeptonPt60','atleast1LooseLepton', '60mll_boosted150','mlj>800','muj'], #muTrigger_boosted','dPhi_lj>2.0'],#'AK8Jets_LSF3>0.75'],
            
            'wr_cross_check_region': ['atleast1tightLepton'],#atleast1AK8Jets'],
            'wr_cross_check_region_withSkims' : ['atleast1AK8Jets','leadTightLeptonPt60'],
            'wr_cross_check_region_withSkims_v1' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800',],
            'wr_cross_check_region_withSkims_v2' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton'],
            'wr_cross_check_region_withSkims_v3' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted'],
            'wr_cross_check_region_withSkims_v4' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted','dPhi_lj>2.0'],
            'wr_cross_check_region_withSkims_v5' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted','dPhi_lj>2.0','atleast1tightLepton'],
            'wr_cross_check_region_withSkims_v6' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted','dPhi_lj>2.0','atleast1tightLepton','notResolved'],
            'wr_cross_check_region_withSkims_mu' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted','dPhi_lj>2.0','muj','notResolved'],
            'wr_cross_check_region_withSkims_emu' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted','dPhi_lj>2.0','emuj','notResolved'],
            'wr_cross_check_region_withSkims_mue' : ['atleast1AK8Jets','leadTightLeptonPt60','mlj>800','atleast1LooseLepton','200mll_boosted','dPhi_lj>2.0','muej','notResolved'],
        }
        #print("Defined selections:", selections.names)

        # Helper: check if all cuts in regions exist in selections
        cutflows = {}

        def check_missing_cuts(selections, regions):
            defined = set(selections.names)
            for region, cuts in regions.items():
                missing = [c for c in cuts if c not in defined]
                if missing:
                    print(f"Region '{region}' has missing selections: {missing}")

        # output["cutflow"] = hist.Hist(
        #     hist.axis.StrCategory([], name="cut", growth=True),
        #     storage=hist.storage.Weight()
        # )

        for region, cuts in regions.items():
            check_missing_cuts(selections, regions)
            # for cut_name in cuts:
            #     cut = selections.all(cut_name)  # Select events passing only this cut
            #     hist_name = f"{region}__{cut_name}"  # Unique histogram name
            #     self.fill_basic_histograms(
            #         output, hist_name, cut, process_name,
            #         AK4Jets, tightLeptons, AK8Jets, looseLeptons, weights
            #     )
            cut = selections.all(*cuts)
            mask = np.ones(len(eventWeight), dtype=bool)
            # n_events = len(tightLeptons)
            # ones = ak.Array(np.ones(n_events, dtype=np.int32))
            # ones = ak.fill_none(ones, 0)
            # ones = ak.Array.to_numpy(ones,allow_missing=True) #awkward_array)
            # tightLeptons is an awkward array per event
            n_events = len(tightLeptons)
            
            # Make an array of ones for each event
            ones = ak.Array(np.ones(n_events, dtype=np.float32))
            
            # If thereâs any chance of None, fill with 0
            ones = ak.fill_none(ones, 0)
            self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tightLeptons, AK8Jets, looseLeptons,ones, mll_boosted,nLeptons,nTightElectrons, nTightMuons, nLooseLeptons, nLooseElectrons, nLooseMuons, nAK8Jets, nAK4Jets, weights)
            cf = {}
            #mask = np.ones(len(eventWeight), dtype=bool)  # start with all events
            i=0
            for cut_name in cuts:
                # i+=1
                # mask = mask & selections.all(cut_name)  # apply one cut at a time
                # cut_single = selections.all(cut_name)
                #cf[cut_name] = np.sum(eventWeight[mask])  # weighted sum after this cut
                # print(cut_name)
                # hist_name = f"{region}__{cut_name}"    # Unique histogram name
                mask = mask & selections.all(cut_name)
                n_evt = np.sum(eventWeight[mask])
                cf[cut_name] = np.sum(eventWeight[mask]) 
                #output["cutflow"].fill(cut=f"{region}__{cut_name}", weight=n_evt)

                # if "boosted" in region :
                #     if i>5 :
                #         self.fill_basic_histograms(
                #         output, hist_name, cut_single, process_name,
                #         AK4Jets, tightLeptons, AK8Jets, looseLeptons, weights
                #     )
            cutflows[region] = cf

        # Pretty print
        import pandas as pd
        for region, cf in cutflows.items():
            print(f"\nCutflow for {region}")
            print(pd.DataFrame.from_dict(cf, orient="index", columns=["Weighted Events"]))
            nested_output = {
                dataset: {
                    **output,
                }
            }
        
        return nested_output
            
    def postprocess(self, accumulator):
        return accumulator
