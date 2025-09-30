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

            ### cutflow histogram
            # ... all your other histograms ...
            'cutflow': self.create_hist('cutflows','process', 'region', (50,0,50),r'cutflows'),
                                        # hist.Hist.new
            # .StrCat([], name='cut', label='Cut')     # one bin per selection
            # .StrCat([], name='process', label='Process')
            # .StrCat([], name='region', label='Region')
            # .Weight()

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
        match = (loose.delta_r(tight)) # #
        #     (abs(loose.pt - ak.fill_none(tight.pt, -999.)) < eps) &
        #     (abs(loose.eta - ak.fill_none(tight.eta, -999.)) < eps) &
        #     (abs(loose.phi - ak.fill_none(tight.phi, -999.)) < eps) &
        #     (loose.charge == ak.fill_none(tight.charge, 999))
        # )
        keep_mask = match >= 0.01
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
        loose_electrons = (events.Electron.pt > 53) & (np.abs(events.Electron.eta) < 2.4) & ((events.Electron.cutBased == 2) | (events.Electron.cutBased_HEEP))
        return events.Electron[loose_electrons]
    def selectLooseMuons(self, events):
        loose_muons = (events.Muon.pt > 53) & (np.abs(events.Muon.eta) < 2.4) & (events.Muon.highPtId == 2)
        return events.Muon[loose_muons]

    def selectAK8Jets(self,events):
        ak8_jets = (events.FatJet.pt > 200) & (np.abs(events.FatJet.eta) < 2.4)  & (events.FatJet.msoftdrop > 40) & (events.FatJet.isTight) 
        return events.FatJet[ak8_jets]

    def selectAK8Jets_withLSF(self,events):
        ak8_jets = (events.FatJet.pt > 200) & (np.abs(events.FatJet.eta) < 2.4)  & (events.FatJet.msoftdrop > 40) & (events.FatJet.isTight) & (events.FatJet.lsf3 > 0.75)
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


    def fill_cutflow(self, output, region, process_name, selections, order, weights=None):
        """
        Fill cutflow histogram for a region.
        
        Parameters
        ----------
        output : dict
        Processor output dictionary with histograms
        region : str
        Region name
        process_name : str
        Dataset/process label
        selections : PackedSelection
        Coffea PackedSelection with masks
        order : list[str]
        List of selection names in order
        weights : Weights or None
        Event weights. If None, unweighted.
        """
        # n_events = len(weights) #next(iter(selections.values())))
        #mask = ak.ones(len(selections[order[0]]), dtype=bool)
        mask = np.ones(len(weights), dtype=bool)
        for cut in order:
            mask = mask & selections.all(cut)
            n_evt = np.sum(weights[mask])
            temp_wt = np.ones(len(mask))
            # if weights is None:
            #     n_events = mask.sum()
            # else:
            #     n_events = weights.weight()[mask].sum()
            # output[hist_name].fill(
	    #     process=process_name,
            #     region=region,
            #     **{axis_name: vals},
            #     weight=w
            # )
            output['cutflow'].fill(
                process=process_name,
                region=region,
                **{'cutflows':n_evt},
                weight=n_evt
            )
            
    def fill_basic_histograms(self, output, region, cut, process_name, jets, leptons, ak8jets, looseleptons, count,mll, mlj, pt_dilept, pt_lj, weights):
        variables =[
            # ('pt_leading_lepton',         leptons[.pt,    'pt_leadlep'),
            # ('eta_leading_lepton',        leptons[:, 0].eta,   'eta_leadlep'),
            # ('phi_leading_lepton',        leptons[:, 0].phi,   'phi_leadlep'),

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
            variables =[
                ('count',         count,    'count'),
            ]
        else:
            variables = [
                ('pt_leading_lepton',         leptons.pt,    'pt_leadlep'),
                ('eta_leading_lepton',        leptons.eta,   'eta_leadlep'),
                ('phi_leading_lepton',        leptons.phi,   'phi_leadlep'),
                ('pt_leading_loose_lepton',      looseleptons.pt,    'pt_leadlooselep'),
                ('eta_leading_loose_lepton',     looseleptons.eta,   'eta_leadlooselep'),
                ('phi_leading_loose_lepton',     looseleptons.phi,   'phi_leadlooselep'),
                ('pt_leading_AK8Jets',            ak8jets.pt,       'pt_leadAK8Jets'),
                ('eta_leading_AK8Jets',           ak8jets.eta,      'eta_leadAK8Jets'),
                ('phi_leading_AK8Jets',           ak8jets.phi,      'phi_leadAK8Jets'),
                ('mass_dilepton',           mll , 'mass_dilepton'),
                ('pt_dilepton',               pt_dilept,   'pt_dilepton'),
                ('mass_twoobject',           mlj , 'mass_twoobject'),
                ('pt_twoobject',             pt_lj,   'pt_twoobject'),
                ('LSF_leading_AK8Jets', ak8jets.lsf3,'LSF_leadingAK8Jets'),
                ('dPhi_leading_tightlepton_AK8Jet',  abs(ak8jets.delta_phi(leptons)),'dPhi_leadTightlep_AK8Jets')
                
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
                eventWeight = eventWeight * sf *58*1000
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
            n_events = len(tightLeptons)
            ones = ak.Array(np.ones(n_events, dtype=np.float32))
            ones = ak.fill_none(ones,0.0)
            self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tightLeptons, AK4Jets, tightLeptons[:,0], ones,ones, ones, ones, ones, weights)

        
        ####  ---- boosted category of events ----- #####
        #### ---- object selections ---  ###
        looseElectrons = self.selectLooseElectrons(events)
        looseMuons = self.selectLooseMuons(events)
        AK8Jets = self.selectAK8Jets(events)
        AK8Jets_withLSF = self.selectAK8Jets_withLSF(events)
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
        
        # ////////////  --- stuff for checking whether resolved or boosted ---- //////
        # //// Making lepton selection  /// #                                                                                                                                
        looseLeptons = ak.with_name(ak.concatenate((looseElectrons, looseMuons), axis=1), 'PtEtaPhiMCandidate')
        looseLeptons = looseLeptons[ak.argsort(looseLeptons.pt, axis=1, ascending=False)]        
        tightLeptons_inc = ak.with_name(ak.concatenate((tightElectrons_inc, tightMuons_inc), axis=1), 'PtEtaPhiMCandidate')
        tightLeptons_inc = tightLeptons_inc[ak.argsort(tightLeptons_inc.pt, axis=1, ascending=False)]

        # For leptons
        has_two_leptons = ak.num(tightLeptons_inc) >= 2
        # pad to 2 muons safely
        muons_padded = ak.pad_none(tightLeptons_inc, 2, axis=1)
        # compute dr only for events with >=2 muons
        dr_l1l2 = ak.where(
            ak.num(tightLeptons_inc) >= 2,
            muons_padded[:,0].delta_r(muons_padded[:,1]),
            ak.full_like(ak.num(tightLeptons_inc), np.nan)
        )
        # For jets
        has_two_jets = ak.num(AK4Jets_inc) >= 2
        ak4jets_padded = ak.pad_none(AK4Jets_inc,2, axis=1)
        dr_j1j2 = ak.where(has_two_jets, ak4jets_padded[:,0].delta_r(ak4jets_padded[:,1]), ak.full_like(has_two_jets, np.nan))

        # dr_jl_min: compute only if both jets and leptons exist
        has_j_and_l = (ak.num(AK4Jets_inc) >= 1) & (ak.num(tightLeptons_inc) >= 1)
        dr_jl_min = ak.where( has_j_and_l, ak.min(AK4Jets_inc[:, :2].nearest(tightLeptons_inc).delta_r(AK4Jets_inc[:, :2]), axis=1), ak.full_like(has_j_and_l, np.nan))
        # Build all 2 leptons × 2 jets pairs
        dr_lj = ak.cartesian({"lep": tightLeptons_inc[:,:2], "jet": AK4Jets_inc[:,:2]}, axis=1)
        dr_lj_vals = dr_lj["lep"].delta_r(dr_lj["jet"])
        
        # Condition: all l-j separations > 0.4
        dr_lj_ok = ak.all(dr_lj_vals > 0.4, axis=1)
        resolved = (((ak.num(tightElectrons_inc)  + (ak.num(tightMuons_inc))) == 2) & (ak.num(AK4Jets_inc) >= 2) & (dr_l1l2 > 0.4) & (dr_j1j2 > 0.4) & (dr_jl_min >0.4)) #(dr_lj_ok))
        #resolved = ((ak.num(tightElectrons_inc) + ak.num(tightMuons_inc)) == 2) & ((ak.num(AK4Jets_inc) >= 2)) & ((dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))
        boosted  = ~resolved
        selections.add("boostedtag",boosted)

        
        ### ---- boosted case ---- ## for now check only for muons, once verified, update it for LEPTONS to include Electrons too ---- ###
        
        # require leading lepton tight
        has_tight_lead = ak.num(tightMuons_inc) > 0 ## for now check only for muons, once verifies, update it for leptons
        lead_pt = ak.firsts(tightMuons_inc.pt)  # safely picks first or None
        lead_is_tight_withpT60 = has_tight_lead & (ak.fill_none(lead_pt > 60, False))
        #selections.add("leadTightwithPt60",lead_is_tight_withpT60) #// ---AAAA update it

        #tightLeptons_inc = tightMuons_inc
        
        tightLepton_padded = ak.pad_none(tightLeptons_inc,1,axis=1)
        tight_lep   = tightLepton_padded[:, 0]
        lead_pdgid  = ak.fill_none(abs(tight_lep.pdgId), 0)
        is_lead_mu  = lead_pdgid == 13
        is_lead_e   = lead_pdgid == 11
        is_tight_pt = tight_lep.pt > 60
        selections.add("leadTightwithPt60",is_tight_pt)
        #selections.add("leadTightwithPt60",lead_is_tight_withpT60)        
        # looseLeptons = looseLeptons[
        #     (looseLeptons.pt != tight_lep.pt) |
        #     (looseLeptons.eta != tight_lep.eta) |
        #     (looseLeptons.phi != tight_lep.phi)
        # ]
        # OR
        looseLeptons = self.remove_lepton(looseLeptons, tight_lep)
        # -- same-flavor and other-flavor loose collections --
        sf_loose = looseLeptons[abs(looseLeptons.pdgId) == abs(tight_lep.pdgId)]
        of_loose = looseLeptons[abs(looseLeptons.pdgId) != abs(tight_lep.pdgId)]
        sf_loose = sf_loose[ak.argsort(sf_loose.pt, axis=1, ascending=False)]
        of_loose = of_loose[ak.argsort(of_loose.pt, axis=1, ascending=False)]
        # ---------------- DY check ----------------
        mll_pairs  = (tight_lep + sf_loose).mass
        mask_mll   = (mll_pairs > 60) & (mll_pairs < 150)
        has_dy_pair = ak.any(mask_mll, axis=1)
        
        # -------- picking loose SF lepton --- #
        #dy_idx        = ak.argmax(mask_mll, axis=1, keepdims=False, mask_identity=True)
        DY_loose_lep  = ak.firsts(sf_loose[mask_mll]) #/// loose SF lepton candidate for DY CR        
        
        # ---------------- AK8 jet candidate ----------------
        AK8Jets = AK8Jets[ak.argsort(AK8Jets.pt, axis=1, ascending=False)]
        #AK8Jets_withLSF = AK8Jets_withLSF[ak.argsort(AK8Jets_withLSF.pt, axis=1, ascending=False)]

        flag_ak8Jet = ak.num(AK8Jets)>=1
        AK8Jets = ak.pad_none(AK8Jets, 1, axis=1)
        dphi       = ak.fill_none(abs(AK8Jets.delta_phi(tight_lep)),0.0)
        has_ak8_dphi_gt2 = ak.any(dphi > 2, axis=1)
        ak8_mask   = dphi > 2.0
        AK8_cand   = ak.firsts(AK8Jets[ak8_mask])   # one per event AK8jet candidate for DY CR
        selections.add("Atleast1AK8Jets & dPhi(J,tightLept)>2", flag_ak8Jet & has_ak8_dphi_gt2 )#&& ak8_mask (~ak.is_none(AK8_cand)))
        
        # ---------------- Case 1: DY CR ----------------
        dr_dy  = AK8_cand.delta_r(DY_loose_lep)
        mlj_dy = ak.where(dr_dy < 0.8,
                          (tight_lep + AK8_cand).mass,
                          (tight_lep + DY_loose_lep + AK8_cand).mass)
        mll_dy = (tight_lep + DY_loose_lep).mass
        pt_dilept_dy = (tight_lep + DY_loose_lep).pt
        pt_lj_dy = ak.where(dr_dy < 0.8,
                          (tight_lep + AK8_cand).pt,
                          (tight_lep + DY_loose_lep + AK8_cand).pt)

        sublead_pdgID = abs(DY_loose_lep.pdgId)
        is_sublead_mu = sublead_pdgID == 13
        is_sublead_e = sublead_pdgID ==11
        DYCR_mask = has_dy_pair & (mlj_dy > 800) #& flag_ak8Jet & has_ak8_dphi_gt2
        selections.add("DYCR_mask", DYCR_mask)
        
        # -------- veto extra tight leptons for DY CR --------
        # ---- remove tight_lep and selected loose candidate from looseLepton collection
        extra_tight_mu = ak.sum(
            (looseMuons.tkRelIso < 0.1) &
            (ak.fill_none(looseMuons.delta_r(tight_lep) > 0.01, True)) &
            (ak.fill_none(looseMuons.delta_r(DY_loose_lep) > 0.01, True)),
            axis=1
        )
        extra_tight_el = ak.sum(
            (looseElectrons.cutBased_HEEP) &
            (ak.fill_none(looseElectrons.delta_r(tight_lep) > 0.01, True)) &
            (ak.fill_none(looseElectrons.delta_r(DY_loose_lep) > 0.01, True)),
            axis=1
        )
        no_extra_tight_dyCR = (extra_tight_mu == 0) & (extra_tight_el == 0)
        
        ## ------ checking if AK8 candiate passes LSF requirement
        flag_lsf =  AK8_cand.lsf3 > 0.75
        selections.add("AK8JetswithLSF",flag_lsf)

        # # ---------------- Case 2: SR (no DY, SF near AK8, no OF near AK8) ----------------
        # flag_ak8Jet_lsf = ak.num(AK8Jets_withLSF)>=1
        # AK8Jets_withLSF = ak.pad_none(AK8Jets_withLSF, 1, axis=1)
        # dphi_lsf       = ak.fill_none(abs(AK8Jets_withLSF.delta_phi(tight_lep)),0.0)
        # has_ak8_dphi_gt2_lsf = ak.any(dphi_lsf > 2, axis=1)
        # ak8_mask_lsf   = dphi_lsf > 2.0
        # AK8_cand   = ak.firsts(AK8Jets_withLSF[ak8_mask_lsf])
        # selections.add("Atleast1AK8Jets & dPhi(J,tightLept)>2", flag_ak8Jet_lsf & has_ak8_dphi_gt2_lsf )
        
        dr_sf = AK8_cand.delta_r(sf_loose)
        mask_sf = dr_sf < 0.8
        sf_candidate = ak.firsts(sf_loose[mask_sf]) # ---- SF lepton candidate passing dR condition
        sf_exist = ak.num(sf_loose[mask_sf])>=1
        dr_of = AK8_cand.delta_r(of_loose) 
        mask_of = dr_of < 0.8
        of_candidate = ak.firsts(of_loose[mask_of]) #  -  ----- OF lepton candidate passing dR condition  
        of_exist = ak.num(of_loose[mask_of])>=1

        is_sr = (~has_dy_pair) & (~ak.is_none(sf_candidate)) & ak.is_none(of_candidate) #sf_exist & (~of_exist) #(~ak.is_none(sf_candidate)) & ak.is_none(of_candidate)
        sublead_pdgID = abs(sf_candidate.pdgId)
        is_sublead_mu_sr = sublead_pdgID == 13
        is_sublead_e_sr = sublead_pdgID ==11
        mlj_sr   = (tight_lep + AK8_cand).mass
        mll_sr = (tight_lep + sf_candidate).mass
        pt_dilept_sr  = (tight_lep + AK8_cand).pt
        pt_lj_sr = (tight_lep + sf_candidate).pt

        SR_mask = is_sr & (mlj_sr > 800) & (mll_sr > 200)
        selections.add("ee(mumu)SR", SR_mask)


        # -------- veto extra tight leptons for SR --------
        extra_tight_mu_sr = ak.sum(
            (looseMuons.tkRelIso < 0.1) &
            (ak.fill_none(looseMuons.delta_r(tight_lep) > 0.01, True)) &
            (ak.fill_none(looseMuons.delta_r(sf_candidate) > 0.01, True)),
            axis=1
        )
        extra_tight_el_sr = ak.sum(
            (looseElectrons.cutBased_HEEP) &
            (ak.fill_none(looseElectrons.delta_r(tight_lep) > 0.01, True)) &
            (ak.fill_none(looseElectrons.delta_r(sf_candidate) > 0.01, True)),
            axis=1
        )
        no_extra_tight_sr = (extra_tight_mu_sr == 0) & (extra_tight_el_sr == 0)
        
        # ---------------- Case 3: Flavor CR (no DY, OF near AK8) ----------------
        is_cr = (~has_dy_pair) & (~ak.is_none(of_candidate))  & ak.is_none(sf_candidate) #(~sf_exist) & of_exist #(~ak.is_none(of_candidate))  & ak.is_none(sf_candidate)
        sublead_pdgID = abs(of_candidate.pdgId)
        is_sublead_mu_cr = sublead_pdgID == 13
        is_sublead_e_cr = sublead_pdgID ==11

        mlj_cr  = (tight_lep + AK8_cand).mass
        mll_cr = (tight_lep + of_candidate).mass
        pt_dilept_cr  = (tight_lep + AK8_cand).pt
        pt_lj_cr = (tight_lep + of_candidate).pt

        CR_mask = is_cr & (mlj_cr > 800) & (mll_cr > 200 )
        selections.add("e(mu) or mu(e)CR", CR_mask)

        
        # -------- veto extra tight leptons for flavor CR --------        
        extra_tight_mu_cr = ak.sum(
            (looseMuons.tkRelIso < 0.1) &
            (ak.fill_none(looseMuons.delta_r(tight_lep) > 0.01, True)) &
            (ak.fill_none(looseMuons.delta_r(of_candidate) > 0.01, True)),
            axis=1
        )
        extra_tight_el_cr = ak.sum(
            (looseElectrons.cutBased_HEEP) &
            (ak.fill_none(looseElectrons.delta_r(tight_lep) > 0.01, True)) &
            (ak.fill_none(looseElectrons.delta_r(of_candidate) > 0.01, True)),
            axis=1
        )
        no_extra_tight_flav_cr = (extra_tight_mu_cr == 0) & (extra_tight_el_cr == 0)

        if mc_campaign in ("RunIISummer20UL18", "Run2Autumn18"):
            eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
            muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100

        # ---------------- Region assignments ----------------
        mumu_dy_cr = muTrig & DYCR_mask & is_lead_mu #& no_extra_tight_dyCR
        ee_dy_cr   = eTrig & DYCR_mask & is_lead_e #& no_extra_tight_dyCR
        
        emu_cr = (eTrig | muTrig) & CR_mask & is_lead_e #& no_extra_tight_flav_cr # lead e, loose mu
        mue_cr = (muTrig | eTrig) & CR_mask & is_lead_mu #& no_extra_tight_flav_cr # lead mu, loose e

        ee_sr = eTrig & SR_mask & is_lead_e #& no_extra_tight_sr
        mumu_sr = muTrig & SR_mask &  is_lead_mu #& no_extra_tight_sr
        selections.add("mumu-dy_cr", mumu_dy_cr & is_sublead_mu)
        selections.add("ee-dy_cr",   ee_dy_cr & is_sublead_e)
        selections.add("mumu_sr", mumu_sr & is_sublead_mu_sr)
        selections.add("ee_sr",   ee_sr & is_sublead_e_sr)
        selections.add("emu-cr",     emu_cr ) #& is_sublead_mu_cr)
        selections.add("mue-cr",     mue_cr ) #& is_sublead_e_cr)
        
        selections.add("allEvents",(resolved) | ~(resolved))

        regions = {
	    'wr_mumu_boosted_dy_cr': ['boostedtag', 'leadTightwithPt60','DYCR_mask','Atleast1AK8Jets & dPhi(J,tightLept)>2','mumu-dy_cr'],
            'wr_mumu_boosted_sr': ['boostedtag', 'leadTightwithPt60','Atleast1AK8Jets & dPhi(J,tightLept)>2','mumu_sr','AK8JetswithLSF'],
            'wr_ee_boosted_dy_cr': ['boostedtag', 'leadTightwithPt60','DYCR_mask','Atleast1AK8Jets & dPhi(J,tightLept)>2','ee-dy_cr'],
            'wr_ee_boosted_sr': ['boostedtag', 'leadTightwithPt60','Atleast1AK8Jets & dPhi(J,tightLept)>2','ee_sr','AK8JetswithLSF'],
            'wr_emu_boosted_flavor_cr': ['boostedtag', 'leadTightwithPt60','Atleast1AK8Jets & dPhi(J,tightLept)>2','emu-cr','AK8JetswithLSF'],
            'wr_mue_boosted_flavor_cr': ['boostedtag', 'leadTightwithPt60','Atleast1AK8Jets & dPhi(J,tightLept)>2','mue-cr','AK8JetswithLSF'],
            
            # 'cross_check_region_nocut' :['allEvents'],
            # 'cross_check_region_notResolved' :['boostedtag'],
            # 'cross_check_region_leadLepMuon': ['boostedtag','leadTightwithPt60'],
            # 'cross_check_region_DYCR': ['boostedtag','leadTightwithPt60', 'DYCR_mask'],
            # 'cross_check_region_DYCR_ak8Jets': ['boostedtag','leadTightwithPt60', 'DYCR_mask','Atleast1AK8Jets & dPhi(J,tightLept)>2'],
            # 'cross_check_region_DYCR_ak8Jets_mlj': ['boostedtag','leadTightwithPt60', 'DYCR_mask','atleast1AK8Jets','dPhi(J,tightLept)>2','DY_mlj>800'],
            # 'cross_check_region_DYCR_ak8Jets_muTrig': ['boostedtag','leadTightwithPt60', 'DYCR_mask','atleast1AK8Jets','dPhi(J,tightLept)>2','DY_mlj>800','mumu-dy_cr'],            
            # 'cross_check_region_SR': ['boostedtag','leadTightwithPt60', ],
            # 'cross_check_region_SR_ak8': ['boostedtag','leadTightwithPt60','Atleast1AK8Jets & dPhi(J,tightLept)>2','dPhi(J,tightLept)>2'],
            # 'cross_check_region_SR_ak8_noextraTight': ['boostedtag','leadTightwithPt60', 'notDYCR','atleast1AK8Jets','dPhi(J,tightLept)>2','noExtraTight'],
            # 'cross_check_region_SR_ak8_noextraTight_loosSF': ['boostedtag','leadTightwithPt60', 'notDYCR','atleast1AK8Jets','dPhi(J,tightLept)>2','noExtraTight'],
            #  'cross_check_region_SR_ak8_noextraTight_loosSF_noOF': ['boostedtag','leadTightwithPt60', 'notDYCR','atleast1AK8Jets','dPhi(J,tightLept)>2','noExtraTight','dR(J,looseL)<0.8','noExtraDiffFlavorLoosetoAK8'],
            # 'cross_check_region_SR_ak8_noextraTight_loosSF_noOF_mll': ['boostedtag','leadTightwithPt60', 'notDYCR','atleast1AK8Jets','dPhi(J,tightLept)>2','noExtraTight','dR(J,looseL)<0.8','noExtraDiffFlavorLoosetoAK8','mumu-dy_cr','200mll_boosted'],
            # 'cross_check_region_SR_ak8_noextraTight_loosSF_noOF_mll_mlj': ['boostedtag','leadTightwithPt60', 'notDYCR','atleast1AK8Jets','dPhi(J,tightLept)>2','noExtraTight','dR(J,looseL)<0.8','noExtraDiffFlavorLoosetoAK8','mumu-dy_cr','200mll_boosted','mlj>800'],
	}
        cutflows = {}
        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            n_events = len(tightLeptons_inc)
            ones = ak.Array(np.ones(n_events, dtype=np.float32))
            ones = ak.fill_none(ones, 0)
            if "dy_cr" in region:
                self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tight_lep, AK8_cand,DY_loose_lep, ones, mll_dy, mlj_dy, pt_dilept_dy, pt_lj_dy, weights)
            elif "flavor_cr" in region :
                self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tight_lep, AK8_cand,of_candidate, ones, mll_cr, mlj_cr, pt_dilept_cr, pt_lj_cr, weights)
            else :
                self.fill_basic_histograms(output, region, cut, process_name, AK4Jets, tight_lep,AK8_cand, sf_candidate, ones, mll_sr, mlj_sr, pt_dilept_sr, pt_lj_sr, weights)
                
            mask = np.ones(len(eventWeight), dtype=bool)
            cf = {}
            i=0
            for cut_name in cuts:
                mask = mask & selections.all(cut_name)
                n_evt = np.sum(eventWeight[mask])
                cf[cut_name] = np.sum(eventWeight[mask])
                
        # cutflow_regions = {
        #     'wr_mumu_boosted_dy_cr': {"cutflow_order": ['boostedtag', 'leadTightwithPt60','60mll_boosted150','atleast1AK8Jets','dPhi(J,tightLept)>2','mlj>800','mumu-dy_cr'],},
        #     'wr_mumu_boosted_sr': { "cutflow_order": ['boostedtag', 'leadTightwithPt60','atleast1AK8Jets','dPhi(J,tightLept)>2','dR(J,looseL)<0.8','mumu-dy_cr','200mll_boosted','mlj>800','AK8JetswithLSF','noExtraTight','noExtraDiffFlavorLoosetoAK8'],},
        # }
        # for region, info in cutflow_regions.items():
        #     order = info["cutflow_order"]
        #     #            print(order)
        #     # Fill cutflow for this region
        #     self.fill_cutflow(output, region, process_name, selections, order, eventWeight)

        # for region, info in cutflow_regions.items():
        #     order = info["cutflow_order"]
        #     print(region, info)
        #     # Weighted cutflow
        #     cf = selections.cutflow(*order, weights=weights)

        #     res = cf.yieldhist(weighted=True)
        #     h_onecut, h_cum = res[0], res[1]
        #     print(res[0],res[1])
        #     output.setdefault("cutflow", processor.dict_accumulator({}))
        #     output["cutflow"].setdefault(region, processor.dict_accumulator({}))
        #     # output["cutflows"][region]["onecut"] = h_onecut
        #     # output["cutflows"][region]["cumulative"] = h_cum
        #     # output.setdefault("cutflow", {})
        #     # output["cutflow"].setdefault(region, {})
        #     output["cutflow"][region]["onecut"] = h_onecut
        #     output["cutflow"][region]["cumulative"] = h_cum

        #     # Unweighted cutflow
        #     cf_unw = selections.cutflow(*order, weights=None)
        #     res_unw = cf_unw.yieldhist(weighted=False)
        #     h_onecut_unw, h_cum_unw = res_unw[0], res_unw[1]
        #     output["cutflow"][region]["onecut_unweighted"] = h_onecut_unw
        #     output["cutflow"][region]["cumulative_unweighted"] = h_cum_unw
        #     print('finishing the cutflow')
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
