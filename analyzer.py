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
import re
import math

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, year='2018', mass_point=None):
        self._year = year
        self._signal_sample = mass_point

        self._triggers = {
            '2018': [
                'HLT_Mu50',
                'HLT_OldMu100',
                'HLT_TkMu100',
                'HLT_Ele32_WPTight_Gsf',
                'HLT_Photon200',
            ],
        }

        self.make_output = lambda: {
            'pt_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='pt_leadlep', label=r'p_{T} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
            'pt_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='pt_subleadlep', label=r'p_{T} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),
#            'pt_leadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 2000, name='pt_leadjet', label=r'p_{T} of the leading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'pt_subleadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 2000, name='pt_subleadjet', label=r'p_{T} of the subleading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'pt_dileptons': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1000, name='pt_dileptons', label=r'p^{T}_{ll} [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'pt_dijets': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1000, name='pt_dijets', label=r'p^{T}_{jj} [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'eta_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(600, -3, 3, name='eta_leadlep', label=r'#eta of the leading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'eta_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(600, -3, 3, name='eta_subleadlep', label=r'#eta of the subleading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'eta_leadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(600, -3, 3, name='eta_leadjet', label=r'#eta of the leading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'eta_subleadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(600, -3, 3, name='eta_subleadjet', label=r'#eta of the subleading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
            'phi_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, -4, 4, name='phi_leadlep', label=r'#phi of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
#            'phi_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(800, -4, 4, name='phi_subleadlep', label=r'#phi of the subleading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'phi_leadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(800, -4, 4, name='phi_leadjet', label=r'#phi of the leading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'phi_subleadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(800, -4, 4, name='phi_subleadjet', label=r'#phi of the subleading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'mass_dileptons': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5000, name='mass_dileptons', label=r'm_{ll} [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'mass_dijets': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5000, name='mass_dijets', label=r'm_{jj} [GeV]'),
#                hist.storage.Weight(),
#            ),
            'mass_threeobject_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='mass_threeobject_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
            'mass_threeobject_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='mass_threeobject_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
            'mass_fourobject': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='mass_fourobject', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
#            'mass_threeobject_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'm_{lljj} [GeV]'),
#                hist.axis.Regular(1600, 0, 8000, name='mass_threeobject_leadlep', label=r'm_{ljj} [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'mass_threeobject_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'm_{lljj} [GeV]'),
#                hist.axis.Regular(1600, 0, 8000, name='mass_threeobject_subleadlep', label=r'm_{ljj} [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'mass_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 2000, name='mass_leadlep', label=r'mass of the leading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'mass_leadjet': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 2000, name='mass_leadjet', label=r'mass of the leading jet [GeV]'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
############################################      naming convention for primed frame hists --> obj_attr_prime_neutrinoLeptonRank
            #2 --- rotated frame 4 obj mass
            'fourobject_mass_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='fourobject_mass_prime_subleadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'fourobject_mass_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 5000, name='fourobject_mass_prime_leadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #3 --- p_parallel_lW
            'leadlep_px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='leadlep_px_prime_subleadlep', label=r'p_{x\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'subleadlep_px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='subleadlep_px_prime_leadlep', label=r'p_{x\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #4 --- p_perp_lW
            'leadlep_py_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='leadlep_py_prime_subleadlep', label=r'p_{y\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'subleadlep_py_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='subleadlep_py_prime_leadlep', label=r'p_{y\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #5 --- p_perp:p_parallel_lW
            'leadlep_py2px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='leadlep_py2px_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'subleadlep_py2px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='subleadlep_py2px_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #6 --- p_parallel:p_trans_lW
            'leadlep_px2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='leadlep_px2pt_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'subleadlep_px2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='subleadlep_px2pt_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #7 --- p_perp:p_trans_lW
            'leadlep_py2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='leadlep_py2pt_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'subleadlep_py2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -10, 10, name='subleadlep_py2pt_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #8 --- p_parallel_lN
            'subleadlep_px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='subleadlep_px_prime_subleadlep', label=r'p_{x\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'leadlep_px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='leadlep_px_prime_leadlep', label=r'p_{x\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #9 --- p_perp_lN
            'subleadlep_py_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='subleadlep_py_prime_subleadlep', label=r'p_{y\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'leadlep_py_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='leadlep_py_prime_leadlep', label=r'p_{y\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #10 --- p_perp:p_parallel_lN
            'subleadlep_py2px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='subleadlep_py2px_prime_subleadlep', label=r'p_{y\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'leadlep_py2px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='leadlep_py2px_prime_leadlep', label=r'p_{y\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #11 --- p_parallel:p_trans_lN
            'subleadlep_px2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='subleadlep_px2pt_prime_subleadlep', label=r'p_{y\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'leadlep_px2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='leadlep_px2pt_prime_leadlep', label=r'p_{y\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #12 --- p_perp:p_trans_lN
            'subleadlep_py2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='subleadlep_py2pt_prime_subleadlep', label=r'p_{y\'} of the subleading lepton [GeV]'),
                hist.storage.Weight(),
            ),

            'leadlep_py2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='leadlep_py2pt_prime_leadlep', label=r'p_{y\'} of the leading lepton [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #13 --- p_parallel_4_obj
            'fourobject_px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='fourobject_px_prime_subleadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'fourobject_px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='fourobject_px_prime_leadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #14 --- p_perp_4_obj
            'fourobject_py_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='fourobject_py_prime_subleadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'fourobject_py_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='fourobject_py_prime_leadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #15 --- p_perp:p_parallel_4_obj
            'fourobject_py2px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='fourobject_py2px_prime_subleadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'fourobject_py2px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='fourobject_py2px_prime_leadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #16 --- p_parallel:p_trans_4_obj
            'fourobject_px2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='fourobject_px2pt_prime_subleadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'fourobject_px2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='fourobject_px2pt_prime_leadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #17 --- p_perp:p_trans_4_obj
            'fourobject_py2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='fourobject_py2pt_prime_subleadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'fourobject_py2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='fourobject_py2pt_prime_leadlep', label=r'm_{lljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #18 --- p_parallel_3_obj
            'threeobject_subleadlep_px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='threeobject_subleadlep_px_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'threeobject_leadlep_px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='threeobject_leadlep_px_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #19 --- p_perp_3_obj
            'threeobject_subleadlep_py_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='threeobject_subleadlep_py_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'threeobject_leadlep_py_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -5000, 5000, name='threeobject_leadlep_py_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #20 --- p_perp:p_parallel_3_obj
            'threeobject_subleadlep_py2px_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='threeobject_subleadlep_py2px_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'threeobject_leadlep_py2px_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='threeobject_leadlep_py2px_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #21 --- p_parallel:p_trans_3_obj
            'threeobject_subleadlep_px2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='threeobject_subleadlep_px2pt_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'threeobject_leadlep_px2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='threeobject_leadlep_px2pt_prime_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
            #22 --- p_perp:p_trans_3_obj
            'threeobject_subleadlep_py2pt_prime_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='threeobject_subleadlep_py2pt_prime_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),

            'threeobject_leadlep_py2pt_prime_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(2000, -50, 50, name='threeobject_leadlep_py2pt_prime_leadlep', label=r'm_{ljj} [GeV]'),
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
        isRealData = not hasattr(events, "genWeight")

        if process == "Signal":
            print(f"Analyzing {dataset} events.")
        elif process in {"SingleMuon", "EGamma"}:
            print(f"Analyzing {len(events)} {process} {dataset} events.")
        else:
            print(f"Analyzing {len(events)} {dataset} events.")

        ####################
        # OBJECT SELECTION #
        ####################

        # muon and electron selections are broken out into standalone functions
        tightElectrons, looseElectrons = selectElectrons(events)
        nTightElectrons = ak.num(tightElectrons)

        tightMuons, looseMuons = selectMuons(events)
        nTightMuons = ak.num(tightMuons)

        AK4Jets, AK8Jets = selectJets(events)
        nAK4Jets = ak.num(AK4Jets)

        tightLeptons, looseElectrons, looseMuons, AK4Jets, AK8Jets = primed_shift(tightElectrons, looseElectrons, tightMuons, looseMuons, AK4Jets, AK8Jets)

        ###########
        # WEIGHTS #
        ###########

        weights = Weights(size=None, storeIndividual=True)
        if not isRealData:
            eventWeight = np.sign(events.genWeight)
        else:
            eventWeight = abs(np.sign(events.event))

        #Only fill histogram with event specific weights
        weights.add("event_weight", weight=eventWeight)

        if not isRealData:
            if process == "Signal":
                output['sumw'] = ak.sum(eventWeight)
            elif process == "DYJets":
                output['sumw'] = events.metadata["genEventSumw"]
        ###################
        # EVENT VARIABLES #
        ###################

        # tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
        # tightLeptons = ak.pad_none(tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)], 2, axis=1)
        # AK4Jets = ak.pad_none(AK4Jets, 2, axis=1)

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
        selections.add("minThreeAK4Jets", (nAK4Jets >= 3))   #add third jet
        selections.add("leadTightLeptonPt60", ((ak.any(tightElectrons.pt > 60, axis=1)) | (ak.any(tightMuons.pt > 60, axis=1))))
        selections.add("mlljj>800", (mlljj > 800))
        selections.add("dr>0.4", (dr_jl_min > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4))

        # Trigger Selections
        eTrig = events.HLT.Ele32_WPTight_Gsf | events.HLT.Photon200 | events.HLT.Ele115_CaloIdVT_GsfTrkIdT
        muTrig = events.HLT.Mu50 | events.HLT.OldMu100 | events.HLT.TkMu100

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

        regions = {
#            'eejj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
#            'mumujj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
#            'emujj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'emujj'],
#            'eejj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'eejj'],
#            'mumujj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'mumujj'],
#            'emujj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'emujj'],
            'eejj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'eejj_400mll3j': ['twoTightLeptons', 'minThreeAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],   #add third jet
#            'mumujj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],
#            'emujj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
        }

        #######################
        # BLIND SIGNAL REGION #
        #######################

        if isRealData:
            for region in ['eejj_400mll', 'mumujj_400mll']:
                if region in regions:
                    del regions[region]

        ##################
        # SIGNAL SAMPLES #
        ##################

        if process == "Signal":
            # Check if the specified mass point is resolved.
            match = re.search(r'MWR(\d+)_MN(\d+)', self._signal_sample)
            if match:
                mwr = int(match.group(1))
                mn = int(match.group(2))
                ratio = mn / mwr
                if ratio < 0.2:
                    raise NotImplementedError(f"Choose a resolved sample (MN/MWR > 0.2). MN/MWR = {ratio:.2f} for this sample.")

            # Add the cut to the specified mass point.
            for mass_point in events.GenModel.fields:
                if self._signal_sample in mass_point:
                    selections.add(f"{self._signal_sample}", eval(f"events.GenModel.WRtoNLtoLLJJ_{self._signal_sample}_TuneCP5_13TeV_madgraph_pythia8==1"))
                    break

            for region in regions:
                regions[region].append(self._signal_sample)

            for region, cuts in regions.items():
                cut = selections.all(*cuts)
                output[f'mlljj_{region}'] = (tightLeptons[cut][:, 0] + tightLeptons[cut][:, 1] + AK4Jets[cut][:, 0] + AK4Jets[cut][:, 1]).mass
                output[f'mljj_leadlep_{region}'] = (tightLeptons[cut][:, 0] + AK4Jets[cut][:, 0] + AK4Jets[cut][:, 1]).mass
                output[f'mljj_subleadlep_{region}'] = (tightLeptons[cut][:, 1] + AK4Jets[cut][:, 0] + AK4Jets[cut][:, 1]).mass
            process = dataset #Not sure why I did this 


        ####################
        # FILL MASS TUPLES #
        ####################

        for region, cuts in regions.items():
            cut = selections.all(*cuts)
            output[f'mlljj_{region}'] = (tightLeptons[cut][:, 0] + tightLeptons[cut][:, 1] + AK4Jets[cut][:, 0] + AK4Jets[cut][:, 1]).mass
            output[f'mljj_leadlep_{region}'] = (tightLeptons[cut][:, 0] + AK4Jets[cut][:, 0] + AK4Jets[cut][:, 1]).mass
            output[f'mljj_subleadlep_{region}'] = (tightLeptons[cut][:, 1] + AK4Jets[cut][:, 0] + AK4Jets[cut][:, 1]).mass

        ###################
        # FILL HISTOGRAMS #
        ###################

        #print(regions.items())

        for region, cuts in regions.items():
            cut = selections.all(*cuts)

            output['pt_leadlep'].fill(
                process=process,
                region=region,
                pt_leadlep=tightLeptons[cut][:, 0].pt,
                weight=weights.weight()[cut],
            )
            output['pt_subleadlep'].fill(
                process=process,
                region=region,
                pt_subleadlep=tightLeptons[cut][:, 1].pt,
                weight=weights.weight()[cut],
            )
#            output['pt_leadjet'].fill(
#                process=process,
#                region=region,
#                pt_leadjet=AK4Jets[cut][:, 0].pt,
#                weight=weights.weight()[cut],
#            )
#            output['pt_subleadjet'].fill(
#                process=process,
#                region=region,
#                pt_subleadjet=AK4Jets[cut][:, 1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['pt_dileptons'].fill(
#                process=process,
#                region=region,
#                pt_dileptons=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['pt_dijets'].fill(
#                process=process,
#                region=region,
#                pt_dijets=(AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['eta_leadlep'].fill(
#                process=process,
#                region=region,
#                eta_leadlep=tightLeptons[cut][:, 0].eta,
#                weight=weights.weight()[cut],
#            )
#            output['eta_subleadlep'].fill(
#                process=process,
#                region=region,
#                eta_subleadlep=tightLeptons[cut][:, 1].eta,
#                weight=weights.weight()[cut],
#            )
#            output['eta_leadjet'].fill(
#                process=process,
#                region=region,
#                eta_leadjet=AK4Jets[cut][:, 0].eta,
#                weight=weights.weight()[cut],
#            )
#            output['eta_subleadjet'].fill(
#                process=process,
#                region=region,
#                eta_subleadjet=AK4Jets[cut][:, 1].eta,
#                weight=weights.weight()[cut],
#            )
            output['phi_leadlep'].fill(
                process=process,
                region=region,
                phi_leadlep=tightLeptons[cut][:, 0].phi,
                weight=weights.weight()[cut],
            )
#            output['phi_subleadlep'].fill(
#                process=process,
#                region=region,
#                phi_subleadlep=tightLeptons[cut][:, 1].phi,
#                weight=weights.weight()[cut],
#            )
#            output['phi_leadjet'].fill(
#                process=process,
#                region=region,
#                phi_leadjet=AK4Jets[cut][:, 0].phi,
#                weight=weights.weight()[cut],
#            )
#            output['phi_subleadjet'].fill(
#                process=process,
#                region=region,
#                phi_subleadjet=AK4Jets[cut][:, 1].phi,
#                weight=weights.weight()[cut],
#            )
#            output['mass_dileptons'].fill(
#                process=process,
#                region=region,
#                mass_dileptons=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['mass_dijets'].fill(
#                process=process,
#                region=region,
#                mass_dijets=(AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                weight=weights.weight()[cut],
#            )
            output['mass_threeobject_leadlep'].fill(
                process=process,
                region=region,
                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
                weight=weights.weight()[cut],
            )
            output['mass_threeobject_subleadlep'].fill(
                process=process,
                region=region,
                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
                weight=weights.weight()[cut],
            )
            output['mass_fourobject'].fill(
                process=process,
                region=region,
                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
                weight=weights.weight()[cut],
            )
#            output['mass_threeobject_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['mass_threeobject_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['mass_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_leadlep=(tightLeptons[cut][:, 0]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['mass_leadjet'].fill(
#                process=process,
#                region=region,
#                mass_leadjet=(AK4Jets[cut][:, 0]).mass,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
############################################      naming convention for primed frame hists --> obj_attr_prime_neutrinoLeptonRank
            #2 -- rotated frame 4 obj mass
            output['fourobject_mass_prime_subleadlep'].fill(
                process=process,
                region=region,
                fourobject_mass_prime_subleadlep=np.sqrt((tightLeptons[cut][:,0].energy + tightLeptons[cut][:,1].energy + AK4Jets[cut][:,0].energy + AK4Jets[cut][:,1].energy)**2 - (tightLeptons[cut][:,0].px_prime_subleadlep + tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)**2 - (tightLeptons[cut][:,0].py_prime_subleadlep + tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)**2 - (tightLeptons[cut][:,0].pz + tightLeptons[cut][:,1].pz + AK4Jets[cut][:,0].pz + AK4Jets[cut][:,1].pz)**2),
                weight=weights.weight()[cut],
            )

            output['fourobject_mass_prime_leadlep'].fill(
                process=process,
                region=region,
                fourobject_mass_prime_leadlep=np.sqrt((tightLeptons[cut][:,0].energy + tightLeptons[cut][:,1].energy + AK4Jets[cut][:,0].energy + AK4Jets[cut][:,1].energy)**2 - (tightLeptons[cut][:,0].px_prime_leadlep + tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)**2 - (tightLeptons[cut][:,0].py_prime_leadlep + tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)**2 - (tightLeptons[cut][:,0].pz + tightLeptons[cut][:,1].pz + AK4Jets[cut][:,0].pz + AK4Jets[cut][:,1].pz)**2),
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #3 --- p_parallel_lW
            output['leadlep_px_prime_subleadlep'].fill(
                process=process,
                region=region,
                leadlep_px_prime_subleadlep=tightLeptons[cut][:,0].px_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['subleadlep_px_prime_leadlep'].fill(
                process=process,
                region=region,
                subleadlep_px_prime_leadlep=tightLeptons[cut][:,1].px_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #4 --- p_perp_lW
            output['leadlep_py_prime_subleadlep'].fill(
                process=process,
                region=region,
                leadlep_py_prime_subleadlep=tightLeptons[cut][:,0].py_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['subleadlep_py_prime_leadlep'].fill(
                process=process,
                region=region,
                subleadlep_py_prime_leadlep=tightLeptons[cut][:,1].py_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #5 --- p_perp:p_parallel_lW
            output['leadlep_py2px_prime_subleadlep'].fill(
                process=process,
                region=region,
                leadlep_py2px_prime_subleadlep=tightLeptons[cut][:,0].py_prime_subleadlep/tightLeptons[cut][:,0].px_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['subleadlep_py2px_prime_leadlep'].fill(
                process=process,
                region=region,
                subleadlep_py2px_prime_leadlep=tightLeptons[cut][:,1].py_prime_leadlep/tightLeptons[cut][:,1].px_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #6 --- p_parallel:p_trans_lW
            output['leadlep_px2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                leadlep_px2pt_prime_subleadlep=tightLeptons[cut][:,0].px_prime_subleadlep/(tightLeptons[cut][:,0].px_prime_subleadlep**2 + tightLeptons[cut][:,0].py_prime_subleadlep**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['subleadlep_px2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                subleadlep_px2pt_prime_leadlep=tightLeptons[cut][:,1].px_prime_leadlep/(tightLeptons[cut][:,1].px_prime_leadlep**2 + tightLeptons[cut][:,1].py_prime_leadlep**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #7 --- p_perp:p_trans_lW
            output['leadlep_py2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                leadlep_py2pt_prime_subleadlep=tightLeptons[cut][:,0].py_prime_subleadlep/(tightLeptons[cut][:,0].px_prime_subleadlep**2 + tightLeptons[cut][:,0].py_prime_subleadlep**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['subleadlep_py2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                subleadlep_py2pt_prime_leadlep=tightLeptons[cut][:,1].py_prime_leadlep/(tightLeptons[cut][:,1].px_prime_leadlep**2 + tightLeptons[cut][:,1].py_prime_leadlep**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #8 --- p_parallel_lN
            output['subleadlep_px_prime_subleadlep'].fill(
                process=process,
                region=region,
                subleadlep_px_prime_subleadlep=tightLeptons[cut][:,1].px_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['leadlep_px_prime_leadlep'].fill(
                process=process,
                region=region,
                leadlep_px_prime_leadlep=tightLeptons[cut][:,0].px_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #9 --- p_perp_lN
            output['subleadlep_py_prime_subleadlep'].fill(
                process=process,
                region=region,
                subleadlep_py_prime_subleadlep=tightLeptons[cut][:,1].py_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['leadlep_py_prime_leadlep'].fill(
                process=process,
                region=region,
                leadlep_py_prime_leadlep=tightLeptons[cut][:,0].py_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #10 --- p_perp:p_parallel_lN
            output['subleadlep_py2px_prime_subleadlep'].fill(
                process=process,
                region=region,
                subleadlep_py2px_prime_subleadlep=tightLeptons[cut][:,1].py_prime_subleadlep/tightLeptons[cut][:,1].px_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['leadlep_py2px_prime_leadlep'].fill(
                process=process,
                region=region,
                leadlep_py2px_prime_leadlep=tightLeptons[cut][:,0].py_prime_leadlep/tightLeptons[cut][:,0].px_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #11 --- p_parallel:p_trans_lN
            output['subleadlep_px2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                subleadlep_px2pt_prime_subleadlep=tightLeptons[cut][:,1].px_prime_subleadlep/(tightLeptons[cut][:,1].px_prime_subleadlep**2 + tightLeptons[cut][:,1].py_prime_subleadlep**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['leadlep_px2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                leadlep_px2pt_prime_leadlep=tightLeptons[cut][:,0].px_prime_leadlep/(tightLeptons[cut][:,0].px_prime_leadlep**2 + tightLeptons[cut][:,0].py_prime_leadlep**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #12 --- p_perp:p_trans_lN
            output['subleadlep_py2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                subleadlep_py2pt_prime_subleadlep=tightLeptons[cut][:,1].py_prime_subleadlep/(tightLeptons[cut][:,1].px_prime_subleadlep**2 + tightLeptons[cut][:,1].py_prime_subleadlep**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['leadlep_py2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                leadlep_py2pt_prime_leadlep=tightLeptons[cut][:,0].py_prime_leadlep/(tightLeptons[cut][:,0].px_prime_leadlep**2 + tightLeptons[cut][:,0].py_prime_leadlep**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #13 --- p_parallel_4_obj
            output['fourobject_px_prime_subleadlep'].fill(
                process=process,
                region=region,
                fourobject_px_prime_subleadlep=tightLeptons[cut][:,0].px_prime_subleadlep + tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['fourobject_px_prime_leadlep'].fill(
                process=process,
                region=region,
                fourobject_px_prime_leadlep=tightLeptons[cut][:,0].px_prime_leadlep + tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #14 --- p_perp_4_obj
            output['fourobject_py_prime_subleadlep'].fill(
                process=process,
                region=region,
                fourobject_py_prime_subleadlep=tightLeptons[cut][:,0].py_prime_subleadlep + tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['fourobject_py_prime_leadlep'].fill(
                process=process,
                region=region,
                fourobject_py_prime_leadlep=tightLeptons[cut][:,0].py_prime_leadlep + tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #15 --- p_perp:p_parallel_4_obj
            output['fourobject_py2px_prime_subleadlep'].fill(
                process=process,
                region=region,
                fourobject_py2px_prime_subleadlep=(tightLeptons[cut][:,0].py_prime_subleadlep + tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)/(tightLeptons[cut][:,0].px_prime_subleadlep + tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep),
                weight=weights.weight()[cut],
            )

            output['fourobject_py2px_prime_leadlep'].fill(
                process=process,
                region=region,
                fourobject_py2px_prime_leadlep=(tightLeptons[cut][:,0].py_prime_leadlep + tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)/(tightLeptons[cut][:,0].px_prime_leadlep + tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep),
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #16 --- p_parallel:p_trans_4_obj
            output['fourobject_px2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                fourobject_px2pt_prime_subleadlep=(tightLeptons[cut][:,0].px_prime_subleadlep + tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)/((tightLeptons[cut][:,0].px_prime_subleadlep + tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)**2 + (tightLeptons[cut][:,0].py_prime_subleadlep + tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['fourobject_px2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                fourobject_px2pt_prime_leadlep=(tightLeptons[cut][:,0].px_prime_leadlep + tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)/((tightLeptons[cut][:,0].px_prime_leadlep + tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)**2 + (tightLeptons[cut][:,0].py_prime_leadlep + tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #17 --- p_perp:p_trans_4_obj
            output['fourobject_py2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                fourobject_py2pt_prime_subleadlep=(tightLeptons[cut][:,0].py_prime_subleadlep + tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)/((tightLeptons[cut][:,0].px_prime_subleadlep + tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)**2 + (tightLeptons[cut][:,0].py_prime_subleadlep + tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['fourobject_py2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                fourobject_py2pt_prime_leadlep=(tightLeptons[cut][:,0].py_prime_leadlep + tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)/((tightLeptons[cut][:,0].px_prime_leadlep + tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)**2 + (tightLeptons[cut][:,0].py_prime_leadlep + tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #18 --- p_parallel_3_obj
            output['threeobject_subleadlep_px_prime_subleadlep'].fill(
                process=process,
                region=region,
                threeobject_subleadlep_px_prime_subleadlep=tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['threeobject_leadlep_px_prime_leadlep'].fill(
                process=process,
                region=region,
                threeobject_leadlep_px_prime_leadlep=tightLeptons[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #19 --- p_perp_3_obj
            output['threeobject_subleadlep_py_prime_subleadlep'].fill(
                process=process,
                region=region,
                threeobject_subleadlep_py_prime_subleadlep=tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep,
                weight=weights.weight()[cut],
            )

            output['threeobject_leadlep_py_prime_leadlep'].fill(
                process=process,
                region=region,
                threeobject_leadlep_py_prime_leadlep=tightLeptons[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #20 --- p_perp:p_parallel_3_obj
            output['threeobject_subleadlep_py2px_prime_subleadlep'].fill(
                process=process,
                region=region,
                threeobject_subleadlep_py2px_prime_subleadlep=(tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)/(tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep),
                weight=weights.weight()[cut],
            )

            output['threeobject_leadlep_py2px_prime_leadlep'].fill(
                process=process,
                region=region,
                threeobject_leadlep_py2px_prime_leadlep=(tightLeptons[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)/(tightLeptons[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep),
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #21 --- p_parallel:p_trans_3_obj
            output['threeobject_subleadlep_px2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                threeobject_subleadlep_px2pt_prime_subleadlep=(tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)/((tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)**2 + (tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['threeobject_leadlep_px2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                threeobject_leadlep_px2pt_prime_leadlep=(tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)/((tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)**2 + (tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
            #22 --- p_perp:p_trans_3_obj
            output['threeobject_subleadlep_py2pt_prime_subleadlep'].fill(
                process=process,
                region=region,
                threeobject_subleadlep_py2pt_prime_subleadlep=(tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)/((tightLeptons[cut][:,1].px_prime_subleadlep + AK4Jets[cut][:,0].px_prime_subleadlep + AK4Jets[cut][:,1].px_prime_subleadlep)**2 + (tightLeptons[cut][:,1].py_prime_subleadlep + AK4Jets[cut][:,0].py_prime_subleadlep + AK4Jets[cut][:,1].py_prime_subleadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )

            output['threeobject_leadlep_py2pt_prime_leadlep'].fill(
                process=process,
                region=region,
                threeobject_leadlep_py2pt_prime_leadlep=(tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)/((tightLeptons[cut][:,1].px_prime_leadlep + AK4Jets[cut][:,0].px_prime_leadlep + AK4Jets[cut][:,1].px_prime_leadlep)**2 + (tightLeptons[cut][:,1].py_prime_leadlep + AK4Jets[cut][:,0].py_prime_leadlep + AK4Jets[cut][:,1].py_prime_leadlep)**2)**0.5,
                weight=weights.weight()[cut],
            )


        output["weightStats"] = weights.weightStatistics
        return output

    def postprocess(self, accumulator):
        return accumulator

###############################################
# Changing to primed frame
#x' axis is along nonneutrino lepton's momentum
###############################################

def maskFunc(column, mask): #for use in dak.map_partitions()
    return column[mask]

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

    tightElectrons = dak.map_partitions(maskFunc, events.Electron, electronSelectTight)
    looseElectrons = dak.map_partitions(maskFunc, events.Electron, electronSelectLoose)

    return tightElectrons, looseElectrons

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

    tightMuons = dak.map_partitions(maskFunc, events.Muon, muonSelectTight)
    looseMuons = dak.map_partitions(maskFunc, events.Muon, muonSelectLoose)

    return tightMuons, looseMuons

def selectJets(events):

    # select AK4 jets
    hem_issue = ((events.Jet.eta <= -3.0) | (events.Jet.eta >= -1.3)) & ((events.Jet.phi <= -1.57) | (events.Jet.phi >= -0.87))

    jetSelectAK4 = (
            (events.Jet.pt > 40)
             & (np.abs(events.Jet.eta) < 2.4)
            & (events.Jet.isTightLeptonVeto)
            & hem_issue
    )

    # select AK8 jets (need to add LSF cut)
    jetSelectAK8 = (
            (events.FatJet.pt > 200)
            & (np.abs(events.FatJet.eta) < 2.4)
            & (events.FatJet.jetId == 2)
            & (events.FatJet.msoftdrop > 40)
            & hem_issue
    )

    AK4Jets = dak.map_partitions(maskFunc, events.Jet, jetSelectAK4)
    AK8Jets = dak.map_partitions(maskFunc, events.Jet, jetSelectAK8)

    return AK4Jets, AK8Jets
                                                                                 ####
def concat(arr1,arr2):                                                              #
    return ak.with_name(ak.concatenate((arr1,arr2), axis=1), 'PtEtaPhiMCandidate')  #
                                                                                    #
def lep_padding(arr):                                                               ##### for use in dak.map_partitions()
    return ak.pad_none(arr[ak.argsort(arr.pt, axis=1, ascending=False)], 2, axis=1) #
                                #FIX PADDING FUNCS TO BE MORE GENERAL               #
def jet_padding(arr):                                                               #
    return ak.pad_none(arr, 2, axis=1)                                              #
                                                                                 ####
def primed_shift (tightElectrons, looseElectrons, tightMuons, looseMuons, AK4Jets, AK8Jets):

    #these dak.map_partitions() don't decrease runtime
    tightLeptons = dak.map_partitions(concat, tightElectrons, tightMuons)
    tightLeptons = dak.map_partitions(lep_padding, tightLeptons)
    AK4Jets = dak.map_partitions(jet_padding, AK4Jets)

    #create the gamma field in the tightLeptons column
    #gamma is the angle between the nonneutrino lepton's xy momentum vector and the positive CMS x-axis
    #tightLeptons[:,0].gamma will give gamma the values assuming that the nonneutrino lepton is the lead lepton
    tightLeptons = dak.with_field(tightLeptons, ak.where(tightLeptons.px > 0,
        np.arctan(tightLeptons.py/tightLeptons.px),
        np.arctan(tightLeptons.py/tightLeptons.px) + np.pi),
        where='gamma')

    #create the primed px of the leptons as a field of the tightLeptons column assuming the neutrino lepton is the sublead lepton
    tightLeptons = dak.with_field(tightLeptons,
            np.cos(tightLeptons[:,0].gamma)*tightLeptons.px + np.sin(tightLeptons[:,0].gamma)*tightLeptons.py,
            where='px_prime_subleadlep')
    #create the primed py of the leptons as a field of the tightLeptons column assuming the neutrino lepton is the sublead lepton
    tightLeptons = dak.with_field(tightLeptons,
            np.sin(tightLeptons[:,0].gamma)*tightLeptons.px*(-1) + np.cos(tightLeptons[:,0].gamma)*tightLeptons.py,
            where='py_prime_subleadlep')

    #create the primed px of the jets as a field of the AK4Jets column assuming the neutrino lepton is the sublead lepton
    AK4Jets = dak.with_field(AK4Jets,
            np.cos(tightLeptons[:,0].gamma)*AK4Jets.px + np.sin(tightLeptons[:,0].gamma)*AK4Jets.py,
            where='px_prime_subleadlep')
    #create the primed py of the jets as a field of the AK4Jets column assuming the neutrino lepton is the sublead lepton
    AK4Jets = dak.with_field(AK4Jets,
            np.sin(tightLeptons[:,0].gamma)*AK4Jets.px*(-1) + np.cos(tightLeptons[:,0].gamma)*AK4Jets.py,
            where='py_prime_subleadlep')



    #create the primed px of the leptons as a field of the tightLeptons column assuming the neutrino lepton is the lead lepton
    tightLeptons = dak.with_field(tightLeptons,
            np.cos(tightLeptons[:,1].gamma)*tightLeptons.px + np.sin(tightLeptons[:,1].gamma)*tightLeptons.py,
            where='px_prime_leadlep')
    #create the primed py of the leptons as a field of the tightLeptons column assuming the neutrino lepton is the lead lepton
    tightLeptons = dak.with_field(tightLeptons,
            np.sin(tightLeptons[:,1].gamma)*tightLeptons.px*(-1) + np.cos(tightLeptons[:,1].gamma)*tightLeptons.py,
            where='py_prime_leadlep')

    #create the primed px of the jets as a field of the AK4Jets column assuming the neutrino lepton is the lead lepton
    AK4Jets = dak.with_field(AK4Jets,
            np.cos(tightLeptons[:,1].gamma)*AK4Jets.px + np.sin(tightLeptons[:,1].gamma)*AK4Jets.py,
            where='px_prime_leadlep')
    #create the primed py of the jets as a field of the AK4Jets column assuming the neutrino lepton is the lead lepton
    AK4Jets = dak.with_field(AK4Jets,
            np.sin(tightLeptons[:,1].gamma)*AK4Jets.px*(-1) + np.cos(tightLeptons[:,1].gamma)*AK4Jets.py,
            where='py_prime_leadlep')

#    num_to_print = 51
#
#    #print the first {num_to_print} elements of the tightLeptons.px column
#    tightLeptons_px_list = tightLeptons.px.head(num_to_print)
#    print(f'tightLeptons.px.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_px_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.py column
#    tightLeptons_py_list = tightLeptons.py.head(num_to_print)
#    print(f'tightLeptons.py.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_py_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.gamma column
#    tightLeptons_gamma_list = tightLeptons.gamma.head(num_to_print)
#    print(f'tightLeptons.gamma.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_gamma_list[i]))
#    
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.pt column
#    tightLeptons_pt_list = tightLeptons.pt.head(num_to_print)
#    print(f'tightLeptons.pt.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_pt_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.px_prime_sublead column
#    tightLeptons_px_prime_sublead_list = tightLeptons.px_prime_sublead.head(num_to_print)
#    print(f'tightLeptons.px_prime_sublead.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_px_prime_sublead_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.py_prime_sublead column
#    tightLeptons_py_prime_sublead_list = tightLeptons.py_prime_sublead.head(num_to_print)
#    print(f'tightLeptons.py_prime_sublead.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_py_prime_sublead_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.px_prime_lead column
#    tightLeptons_px_prime_lead_list = tightLeptons.px_prime_lead.head(num_to_print)
#    print(f'tightLeptons.px_prime_lead.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_px_prime_lead_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')
#
#    #print the first {num_to_print} elements of the tightLeptons.py_prime_lead column
#    tightLeptons_py_prime_lead_list = tightLeptons.py_prime_lead.head(num_to_print)
#    print(f'tightLeptons.py_prime_lead.head({num_to_print}): ')
#    for i in range (0,num_to_print):
#        print(str(i) + ' --> ' + str(tightLeptons_py_prime_lead_list[i]))
#
#    print()
#    print('---------------------------------------------------------------------------------------------------------------------')

    return tightLeptons, looseElectrons, looseMuons, AK4Jets, AK8Jets



#print('muon.e:')
#print(events.Muon.e.compute())
#print('muon.e length = ' + str(len(events.Muon.e.compute())))
#print('electron.e:')
#print(events.Electron.e.compute())
#print('electron.e length = ' + str(len(events.Electron.e.compute())))
#print('jet.e')
#print(events.Jet.e.compute())
#print('jet.e length = ' + str(len(events.Jet.e.compute())))
