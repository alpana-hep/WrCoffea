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

            ### Histograms for boosted 
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

    def remove_lepton(self,loose, tight):
        # boolean mask: keep loose leptons that are not exactly the chosen tight                                                                                         
        # (compare by index: remove the one with same pt, eta, phi, charge)                                                                                              
        # mask = ~((loose.pt == tight.pt) &
	#          (loose.eta == tight.eta) &
        #          (loose.phi == tight.phi) &
	#          (loose.charge == tight.charge))
        eps = 1e-6
        match = (
            (abs(loose.pt - ak.fill_none(tight.pt, -999.)) < eps) &
            (abs(loose.eta - ak.fill_none(tight.eta, -999.)) < eps) &
            (abs(loose.phi - ak.fill_none(tight.phi, -999.)) < eps) &
            (loose.charge == ak.fill_none(tight.charge, 999))
        )
        keep_mask = ~match
        return loose[keep_mask]

    def selectElectrons(self, events):
        tight_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.cutBased_HEEP)
        loose_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & (events.Electron.cutBased == 2)
        return events.Electron[tight_electrons], events.Electron[loose_electrons]

    def selectMuons(self, events):
        tight_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2) & (events.Muon.tkRelIso < 0.1)
        loose_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2)
        return events.Muon[tight_muons], events.Muon[loose_muons]

    def selectJets(self, events):
        ak4_jets = (events.Jet.pt > 40) & (np.abs(events.Jet.eta) < 2.4) & (events.Jet.isTightLeptonVeto)
        return events.Jet[ak4_jets]

    ### ----- Boosted Helper functions ----------- ###
    def selectLooseElectrons(self, events):
        loose_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4)
        return events.Electron[loose_electrons]
    def selectLooseMuons(self, events):
        loose_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2)
        return events.Muon[loose_muons]

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
        selections.add("minTwoAK4Jets", ak.num(AK4Jets) >= 2)
        selections.add("leadTightLeptonPt60", (ak.any(tightElectrons.pt > 60, axis=1) | ak.any(tightMuons.pt > 60, axis=1)))
        selections.add("mlljj>800", mlljj > 800)
        selections.add("dr>0.4", (dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

    def fill_basic_histograms(self, output, region, cut, process_name, jets, leptons, ak8jets, looseleptons, weights):
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
        else:
            variables = [
                ('pt_leading_lepton',         leptons[:, 0].pt,    'pt_leadlep'),
                ('eta_leading_lepton',        leptons[:, 0].eta,   'eta_leadlep'),
                ('phi_leading_lepton',        leptons[:, 0].phi,   'phi_leadlep'),
                ('pt_leading_loose_lepton',      looseleptons.pt,    'pt_leadlooselep'),
                ('eta_leading_loose_lepton',     looseleptons.eta,   'eta_leadlooselep'),
                ('phi_leading_loose_lepton',     looseleptons.phi,   'phi_leadlooselep'),
                ('pt_leading_AK8Jets',            ak8jets[:, 0].pt,       'pt_leadAK8Jets'),
                ('eta_leading_AK8Jets',           ak8jets[:, 0].eta,      'eta_leadAK8Jets'),
                ('phi_leading_AK8Jets',           ak8jets[:, 0].phi,      'phi_leadAK8Jets'),
                ('mass_dilepton',           (leptons[:, 0] + looseleptons).mass , 'mass_dilepton'),
                ('pt_dilepton',               (leptons[:, 0] + looseleptons).pt,   'pt_dilepton'),
                ('mass_twoobject',           (leptons[:, 0] + ak8jets[:, 0]).mass , 'mass_twoobject'),
                ('pt_twoobject',             (leptons[:, 0] + ak8jets[:, 0]).pt,   'pt_twoobject'),
                ('LSF_leading_AK8Jets', ak8jets[:,0].lsf3,'LSF_leadingAK8Jets'),
                ('dPhi_leading_tightlepton_AK8Jet',  ak8jets[:, 0].delta_phi(leptons[:,0]),'dPhi_leadTightlep_AK8Jets')
            ]

        if self.variable is not None:
            for _, vals_array, axis_name in variables:
                if axis_name == self.variable:
                    vals_all = vals_array
                    break

        for hist_name, values, axis_name in variables:
            vals = values[cut]
            w = weights.weight()[cut]

            if process_name == "DYJets" and self.lookup_EE is not None:
                if region.startswith("wr_ee_resolved_dy_cr") or region.startswith("wr_ee_resolved_sr"):
                    corr = self.lookup_EE(vals_all[cut])
                elif region.startswith("wr_mumu_resolved_dy_cr") or region.startswith("wr_mumu_resolved_sr"):
                    corr = self.lookup_MM(vals_all[cut])
                else:
                    corr = 1.0
                w = w * corr

            output[hist_name].fill(
                process=process_name,
                region=region,
                **{axis_name: vals},
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

        # Object selection
        tightElectrons, _ = self.selectElectrons(events)
        nTightElectrons = ak.num(tightElectrons)

        tightMuons, _ = self.selectMuons(events)
        nTightMuons = ak.num(tightMuons)

        AK4Jets = self.selectJets(events)
        nAK4Jets = ak.num(AK4Jets)

        # Event variables
        tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons = ak.pad_none(tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)], 2, axis=1)

        AK4Jets = ak.pad_none(AK4Jets, 2, axis=1)
        mjj = ak.fill_none((AK4Jets[:, 0] + AK4Jets[:, 1]).mass, False)

        mll = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1]).mass, False)
        mlljj = ak.fill_none((tightLeptons[:, 0] + tightLeptons[:, 1] + AK4Jets[:, 0] + AK4Jets[:, 1]).mass, False)

        dr_jl_min = ak.fill_none(ak.min(AK4Jets[:, :2].nearest(tightLeptons).delta_r(AK4Jets[:, :2]), axis=1), False)
        dr_j1j2 = ak.fill_none(AK4Jets[:, 0].delta_r(AK4Jets[:, 1]), False)
        dr_l1l2 = ak.fill_none(tightLeptons[:, 0].delta_r(tightLeptons[:, 1]), False)

        # Event selections
        selections = PackedSelection()
        self.add_resolved_selections(selections, tightElectrons, tightMuons, AK4Jets, mlljj, dr_jl_min, dr_j1j2, dr_l1l2)

        # Trigger selections
        if mc_campaign in ("RunIISummer20UL18", "Run2Autumn18"):
            eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
            muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100
            selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
            selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
            selections.add("emuTrigger", (eTrig & muTrig & (nTightElectrons == 1) & (nTightMuons == 1)))
        elif mc_campaign in ("Run3Summer22", "Run3Summer23BPix", "Run3Summer22EE", "Run3Summer23"):
            eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
            muTrig = events.HLT.Mu50 | events.HLT.HighPtTkMu100
            selections.add("eeTrigger", (eTrig & (nTightElectrons == 2) & (nTightMuons == 0)))
            selections.add("mumuTrigger", (muTrig & (nTightElectrons == 0) & (nTightMuons == 2)))
            selections.add("emuTrigger", ((eTrig | muTrig) & (nTightElectrons == 1) & (nTightMuons == 1)))

        # Event Weights
        weights = Weights(len(events))
        if not (not hasattr(events, "genWeight")):  # is MC
            eventWeight = abs(np.sign(events.event))
            if mc_campaign == "RunIISummer20UL18" and process_name == "DYJets":
                eventWeight = eventWeight * 1.35

            if process_name != "Signal":
                sf = metadata['xsec'] / metadata['nevts']
                eventWeight = eventWeight * sf * 58.9 *1000
            else:
                sf = metadata['xsec'] / metadata['nevts']
                eventWeight = eventWeight * sf
        else:
            eventWeight = abs(np.sign(events.event))

        weights.add("event_weight", weight=eventWeight)

        selections.add("eejj", ((ak.num(tightElectrons) == 2) & (ak.num(tightMuons) == 0)))
        selections.add("mumujj", ((ak.num(tightElectrons) == 0) & (ak.num(tightMuons) == 2)))
        selections.add("emujj", ((ak.num(tightElectrons) == 1) & (ak.num(tightMuons) == 1)))

        # mll selections
        selections.add("60mll150", ((mll > 60) & (mll < 150)))
        selections.add("400mll", (mll > 400))

        # Define regions
        regions = {
            'wr_ee_resolved_dy_cr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
            'wr_mumu_resolved_dy_cr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
            'wr_resolved_flavor_cr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
            'wr_ee_resolved_sr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'wr_mumu_resolved_sr': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],
        }

        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tightLeptons, AK4Jets, tightLeptons[:,0], weights)

        
        ####  ---- boosted category of events ----- #####
        #### ---- object selections ---  ###
        looseElectrons = self.selectLooseElectrons(events)
        looseMuons = self.selectLooseMuons(events)
        AK8Jets = self.selectAK8Jets(events)
        AK4Jets_inc = self.selectJets(events)
        # define tight by querying loose
        tight_mask_e = (looseElectrons.cutBased_HEEP) 
        tightElectrons_inc = looseElectrons[tight_mask_e]
        
        ## -- tight muons --- ##

        tight_mask_mu = (looseMuons.tkRelIso < 0.1)
        tightMuons_inc = looseMuons[tight_mask_mu]
        tightMuons_inc = tightMuons_inc[ak.argsort(tightMuons_inc.pt, axis=1, ascending=False)]
        flag_check = (ak.num(tightMuons_inc) != ak.num(tightMuons))
        #print('print me ', flag_check[flag_check==True], tight_mask_mu[tight_mask_mu==False])
        # For leptons
        has_two_leptons = ak.num(tightMuons_inc) >= 2
        # dr_l1l2 = ak.where(has_two_leptons, tightMuons_inc[:,0].delta_r(tightMuons_inc[:,1]), ak.full_like(has_two_leptons, np.nan))

        # pad to 2 muons safely
        muons_padded = ak.pad_none(tightMuons_inc, 2, axis=1)

        # compute dr only for events with >=2 muons
        dr_l1l2 = ak.where(
            ak.num(tightMuons_inc) >= 2,
            muons_padded[:,0].delta_r(muons_padded[:,1]),
            ak.full_like(ak.num(tightMuons_inc), np.nan)
        )
        # For jets
        has_two_jets = ak.num(AK4Jets_inc) >= 2
        ak4jets_padded = ak.pad_none(AK4Jets_inc,2, axis=1)
        dr_j1j2 = ak.where( has_two_jets, ak4jets_padded[:,0].delta_r(ak4jets_padded[:,1]), ak.full_like(has_two_jets, np.nan))

        # dr_jl_min: compute only if both jets and leptons exist
        has_j_and_l = (ak.num(AK4Jets_inc) >= 1) & (ak.num(tightMuons_inc) >= 1)
        dr_jl_min = ak.where( has_j_and_l, ak.min(AK4Jets_inc[:, :2].nearest(tightMuons_inc).delta_r(AK4Jets_inc[:, :2]), axis=1), ak.full_like(has_j_and_l, np.nan))
        resolved = ((ak.num(tightMuons_inc) == 2) & (ak.num(AK4Jets_inc) >= 2) & (dr_l1l2 > 0.4) & (dr_j1j2 > 0.4) & (dr_jl_min > 0.4))
        #resolved = ((ak.num(tightElectrons_inc) + ak.num(tightMuons_inc)) == 2) & ((ak.num(AK4Jets_inc) >= 2)) & ((dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))
        boosted  = ~resolved
        selections.add("boostedtag",boosted)
        n_total = len(events)
        n_resolved = ak.sum(resolved)
        n_boosted = ak.sum(boosted)
        
        print("Total:", n_total)
        print("Resolved:", n_resolved)
        print("Boosted (~resolved):", n_boosted)
        
        looseLeptons = ak.with_name(ak.concatenate((looseElectrons, looseMuons), axis=1), 'PtEtaPhiMCandidate')
        looseLeptons = looseLeptons[ak.argsort(looseLeptons.pt, axis=1, ascending=False)]

        tightLeptons_inc = ak.with_name(ak.concatenate((tightElectrons_inc, tightMuons_inc), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons_inc = tightLeptons_inc[ak.argsort(tightLeptons_inc.pt, axis=1, ascending=False)]

        ### ---- boosted case ---- ## for now check only for muons, once verified, update it for LEPTONS to include Electrons too ---- ###

        
        # require leading lepton tight
        has_tight_lead = ak.num(tightMuons_inc) > 0 ## for now check only for muons, once verifies, update it for leptons
        lead_pt = ak.firsts(tightMuons_inc.pt)  # safely picks first or None
        lead_is_tight_withpT60 = has_tight_lead & (ak.fill_none(lead_pt > 60, False))

        selections.add("leadTightwithPt60",lead_is_tight_withpT60)

        
        # find subleading loose lepton
        has_sub_loose = ak.num(looseLeptons) > 1
        
        # now check that beyond the first two loose leptons, no extra tight exists                                                                                 
        extra_tight_electron = ak.sum(looseElectrons[:,2:].cutBased_HEEP, axis=1)   # for electrons 
        extra_tight_muon = ak.sum(looseMuons[:,2:].tkRelIso < 0.1, axis=1)   # for Muons
                
        flag_noextra = (extra_tight_electron == 0) & (extra_tight_muon == 0)
        valid_events = flag_noextra ### for now keep it simple,  boosted & has_sub_loose & lead_is_tight_withpT60 & flag_noextra

        selections.add("noExtraTight",valid_events)
        
        
        flag_ak8 = (ak.num(AK8Jets) >= 1)
        selections.add("atleast1AK8Jets",flag_ak8)

        ### padding these as next calulcations will make coffea yell at you!!!!!!
        AK8Jets = ak.pad_none(AK8Jets, 1, axis=1)
        tightMuons_inc = ak.pad_none(tightMuons_inc,1,axis=1)
        looseMuons = ak.pad_none(looseMuons,2,axis=1)
        tightElectrons_inc = ak.pad_none(tightElectrons_inc,1,axis=1)
        looseElectrons = ak.pad_none(looseElectrons,2,axis=1)
        looseLeptons = ak.pad_none(looseLeptons,3,axis=1)
        
        # get first jet's lsf3 safely
        first_lsf = ak.firsts(AK8Jets.lsf3)  # returns None if no jet        
        # fill None with 0.0 (or False)
        first_lsf_safe = ak.fill_none(first_lsf, 0.0)
        # define flag
        flag_lsf = flag_ak8 & (first_lsf_safe > 0.75)
        selections.add("AK8JetswithLSF",flag_lsf)

        dphi = ak.fill_none(abs(AK8Jets[:,0].delta_phi(tightMuons_inc[:,0])),0.0)
        #dphi_ak8TightLep = ak.fill_none(dphi,0.0)
        flag_dphi = (dphi > 2.0)
        selections.add("dPhi(J,tightLept)>2",flag_dphi)
        

        dr_sub = ak.fill_none(AK8Jets[:,0].delta_r(looseMuons[:,1:]),9)
        #dr_ak8LooseLept = ak.fill_none(dr_sub,9)
        flag_dr_ak8loose = ak.any(dr_sub < 0.8, axis=1)  # axis=1 over sub_muons
        flag_dr_ak8loose = ak.fill_none(flag_dr_ak8loose, False)
        selections.add("dR(J,looseL)<0.8", flag_dr_ak8loose)
        
        
        # dR to all other-flavor loose leptons
        extraElectrons = looseElectrons[:, 2:]  # shape: [events, #extra_e]
        extraMuons     = looseMuons[:, 2:]      # shape: [events, #extra_mu]
        
        # dR for extra electrons
        dr_extra_e = ak.min(AK8Jets[:,0].delta_r(extraElectrons), axis=1)
        dr_extra_m = ak.min(AK8Jets[:,0].delta_r(extraMuons), axis=1)
        dr_extra_e = ak.fill_none(dr_extra_e, 999.0)
        dr_extra_m = ak.fill_none(dr_extra_m, 999.0)
        # -------------------------------
        # consider all subleading loose leptons
        sub_loose_muons = looseMuons[:, 1:]       # skip leading
        sub_loose_elec  = looseElectrons[:, 1:]
        
        # dR to leading AK8 jet (padded, safe)
        dr_sub_muons = AK8Jets[:,0].delta_r(sub_loose_muons)
        dr_sub_elec  = AK8Jets[:,0].delta_r(sub_loose_elec)        
        # mask for leptons passing dR < 0.8
        mask_muons = dr_sub_muons < 0.8
        mask_elec  = dr_sub_elec  < 0.8
        
        # pick **first subleading loose lepton passing dR<0.8 per event
        sublead_loose_mu = ak.firsts(sub_loose_muons[mask_muons])
        sublead_loose_e  = ak.firsts(sub_loose_elec[mask_elec])
        
        # flavor of chosen subleading loose lepton
        #sublead_pdgid = ak.fill_none(ak.where(ak.num(sublead_loose_mu) > 0, 13, ak.where(ak.num(sublead_loose_e) > 0, 11, 0)), 0)
        #sublead_pdgid = ak.fill_none(ak.where(sublead_loose_mu != None, 13,ak.where(sublead_loose_e != None, 11, 0)), 0)
        sublead_pdgid = ak.fill_none(
            ak.where(~ak.is_none(sublead_loose_mu), abs(sublead_loose_mu.pdgId),
                     ak.where(~ak.is_none(sublead_loose_e), abs(sublead_loose_e), 0)),
            0
        )
        flag_no_extra_close = ((sublead_pdgid == 11) & (dr_extra_m > 0.8)) | ((sublead_pdgid == 13) & (dr_extra_e > 0.8))                                                            
        selections.add("noExtraDiffFlavorLoosetoAK8", flag_no_extra_close)

        
        is_sub_mu = sublead_pdgid == 13
        is_sub_e  = sublead_pdgid == 11
        

        # flavor of leading tight lepton
        lead_pdgid = ak.fill_none(abs(tightMuons_inc[:,0].pdgId), 0)
        is_lead_e  = lead_pdgid == 11
        is_lead_mu = lead_pdgid == 13
        
        # regions based on (lead tight, sub loose) flavor
        mumu_dy_cr = is_lead_mu #& is_sub_mu #& flag_no_extra_close
        emu_cr     = is_lead_e  & is_sub_mu & flag_no_extra_close
        mue_cr     = is_lead_mu & is_sub_e  & flag_no_extra_close
        ee_dy_cr   = is_lead_e  #& is_sub_e  & flag_no_extra_close  # optional
        
        
        selections.add("mumu-dy_cr", mumu_dy_cr)
        selections.add("emu-cr",     emu_cr)
        selections.add("mue-cr",     mue_cr)
        selections.add("ee-dy_cr",   ee_dy_cr)
        

        #loose_others = ak.where(~ak.is_none(tightMuons_inc[:,0]), 
        #                       self.remove_lepton(looseMuons, tightMuons_inc[:,0]), 
        #                      looseMuons)
        
        # Step 3: pick the highest-pT leftover loose lepton
        # other_lep = looseMuons[~tight_mask_mu] #ak.firsts(loose_others)
        # other_lep = ak.fill_none(other_lep[ak.argsort(other_lep.pt, axis=1,ascending=False)],False)
        # other_lead_lep = ak.firsts(other_lep) 
        ### - calculating invariant mass ----- #####
        
        leading_tight = tightMuons_inc[:, 0]
        looseMuons_wo_tight = self.remove_lepton(looseMuons, leading_tight)
        
        mll_boosted = ak.fill_none((tightMuons_inc[:, 0] + looseMuons_wo_tight[:,0]).mass, 0.0)
        mlj_boosted = ak.fill_none((tightMuons_inc[:, 0] + AK8Jets[:,0]).mass, 0.0)
        selections.add("60mll_boosted150",((mll_boosted > 60) & (mll_boosted < 150)))
        selections.add("200mll_boosted",(mll_boosted > 200))
        selections.add("mlj>800",(mlj_boosted > 800))

        ## special thing for DY CR
        tight_lep = tightMuons_inc[:, 0]  # pick leading tight lepton
        mll_pairs = (tight_lep[:, None] + looseMuons).mass
        has_dy_pair = ak.fill_none(ak.any((mll_pairs > 60) & (mll_pairs < 150), axis=1), True)
        #print(has_dy_pair)
        selections.add("DYCR", has_dy_pair)
        # mll_pairs = (tightMuons_inc[:, None] + looseMuons).mass
        # valid_counts = ak.sum((mll_pairs > 60) & (mll_pairs < 150), axis=1)
        # has_dy_pair = valid_counts >0 #ak.fill_none(ak.any((mll_pairs > 60) & (mll_pairs < 150), axis=1), False)
        # selections.add("DYCR", has_dy_pair)
        #n_pass = ak.sum(all_flags)
        #print("Total events passing flags:", n_pass)
        
        regions = {
	    'wr_mumu_boosted_dy_cr': ['boostedtag', 'leadTightwithPt60','60mll_boosted150','atleast1AK8Jets','dPhi(J,tightLept)>2','mlj>800','mumu-dy_cr'],
            'wr_mumu_boosted_sr': ['boostedtag', 'leadTightwithPt60','atleast1AK8Jets','dPhi(J,tightLept)>2','dR(J,looseL)<0.8','mumu-dy_cr','200mll_boosted','mlj>800','AK8JetswithLSF','noExtraTight','noExtraDiffFlavorLoosetoAK8'],
	}
        cutflows = {}
        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tightMuons_inc, AK8Jets,looseMuons_wo_tight[:,0], weights)
            mask = np.ones(len(eventWeight), dtype=bool)
            cf = {}
            i=0
            for cut_name in cuts:
                mask = mask & selections.all(cut_name)
                n_evt = np.sum(eventWeight[mask])
                cf[cut_name] = np.sum(eventWeight[mask])
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
