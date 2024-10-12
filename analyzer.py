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
from utils.prime_frame import *

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
#            'pt_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 2000, name='pt_leadlep', label=r'p_{T} of the leading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'pt_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 2000, name='pt_subleadlep', label=r'p_{T} of the subleading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
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
#            'phi_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(800, -4, 4, name='phi_leadlep', label=r'#phi of the leading lepton [GeV]'),
#                hist.storage.Weight(),
#            ),
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
                hist.axis.Regular(1000, 0, 3000, name='mass_threeobject_leadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
            'mass_threeobject_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 3000, name='mass_threeobject_subleadlep', label=r'm_{ljj} [GeV]'),
                hist.storage.Weight(),
            ),
            'mass_fourobject': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 3000, name='mass_fourobject', label=r'm_{lljj} [GeV]'),
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
#            'var_1_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1400, name='var_1_leadlep', label=r'var_1_leadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_1_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1400, name='var_1_subleadlep', label=r'var_1_subleadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_1 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1400, name='var_1', label=r'var_1 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_1 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1400, name='var_1', label=r'var_1 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_3_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_3_leadlep', label=r'var_3_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_3_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_3_subleadlep', label=r'var_3_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_3 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_3', label=r'var_3 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_3 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_3', label=r'var_3 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_4_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_4_leadlep', label=r'var_4_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_4_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_4_subleadlep', label=r'var_4_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_4 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_4', label=r'var_4 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_4 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_4', label=r'var_4 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_7_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_7_leadlep', label=r'var_7_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_7_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_7_subleadlep', label=r'var_7_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_7 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_7', label=r'var_7 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_7 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 2500, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 40, name='var_7', label=r'var_7 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_14_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 5000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 10000000, name='var_14_leadlep', label='$\mathrm{var_14_leadlep [GeV^2]}$'),
#                hist.storage.Weight(),
#            ),
#            'var_14_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 5000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 10000000, name='var_14_subleadlep', label='$\mathrm{var_14_subleadlep [GeV^2]}$'),
#                hist.storage.Weight(),
#            ),
#            'var_14 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 5000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 10000000, name='var_14', label='$\mathrm{var_14 [GeV^2]}$'),
#                hist.storage.Weight(),
#            ),
#            'var_14 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 5000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 10000000, name='var_14', label='$\mathrm{var_14 [GeV^2]}$'),
#                hist.storage.Weight(),
#            ),
#            'var_18_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 800, name='var_18_leadlep', label=r'var_18_leadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_18_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 800, name='var_18_subleadlep', label=r'var_18_subleadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_18 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 800, name='var_18', label=r'var_18 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_18 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 800, name='var_18', label=r'var_18 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_23_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_23_leadlep', label=r'var_23_leadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_23_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_23_subleadlep', label=r'var_23_subleadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_23 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_23', label=r'var_23 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_23 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_23', label=r'var_23 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_24_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_24_leadlep', label=r'var_24_leadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_24_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_24_subleadlep', label=r'var_24_subleadlep [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_24 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_24', label=r'var_24 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_24 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 4500, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_24', label=r'var_24 [GeV]'),
#                hist.storage.Weight(),
#            ),
#            'var_27_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_27_leadlep', label=r'var_27_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_27_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_27_subleadlep', label=r'var_27_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_27 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_27', label=r'var_27 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_27 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_27', label=r'var_27 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_28_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 5, name='var_28_leadlep', label=r'var_28_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_28_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 5, name='var_28_subleadlep', label=r'var_28_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_28 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 5, name='var_28', label=r'var_28 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_28 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 5, name='var_28', label=r'var_28 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_29_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_29_leadlep', label=r'var_29_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_29_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_29_subleadlep', label=r'var_29_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_29 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_29', label=r'var_29 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_29 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_29', label=r'var_29 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_30_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 25, name='var_30_leadlep', label=r'var_30_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_30_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 25, name='var_30_subleadlep', label=r'var_30_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_30 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 25, name='var_30', label=r'var_30 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_30 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 25, name='var_30', label=r'var_30 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_31_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_31_leadlep', label=r'var_31_leadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_31_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_31_subleadlep', label=r'var_31_subleadlep [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_31 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_31', label=r'var_31 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_31 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_31', label=r'var_31 [unitless]'),
#                hist.storage.Weight(),
#            ),
#            'var_32_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_32_leadlep', label=r'var_32_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_32_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_32_subleadlep', label=r'var_32_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_32 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_32', label=r'var_32'),
#                hist.storage.Weight(),
#            ),
#            'var_32 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_32', label=r'var_32'),
#                hist.storage.Weight(),
#            ),
#            'var_33_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(300, 0.000001, 1, name='var_33_leadlep', label=r'var_33_leadlep', transform=hist.axis.transform.log),
#                hist.storage.Weight(),
#            ),
#            'var_33_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 3000, name='var_33_subleadlep', label=r'var_33_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_33 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_33', label=r'var_33'),
#                hist.storage.Weight(),
#            ),
#            'var_33 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 0.001, name='var_33', label=r'var_33'),
#                hist.storage.Weight(),
#            ),
#            'var_34 vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1000, name='var_34', label=r'var_34'),
#                hist.storage.Weight(),
#            ),
#            'var_34 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1000, name='var_34', label=r'var_34'),
#                hist.storage.Weight(),
#            ),
#            'var_34 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 1000, name='var_34', label=r'var_34'),
#                hist.storage.Weight(),
#            ),
#            'var_35 vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 2000, name='var_35', label=r'var_35'),
#                hist.storage.Weight(),
#            ),
#            'var_35 vs. mass_threeobject_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_threeobject_leadlep', label=r'mass_threeobject_leadlep [GeV]'),
#                hist.axis.Regular(200, 0, 2000, name='var_35', label=r'var_35'),
#                hist.storage.Weight(),
#            ),
#            'var_35 vs. mass_threeobject_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_threeobject_subleadlep', label=r'mass_threeobject_subleadlep [GeV]'),
#                hist.axis.Regular(200, 0, 2000, name='var_35', label=r'var_35'),
#                hist.storage.Weight(),
#            ),
            'var_36': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 10, name='var_36', label=r'var_36'),
                hist.storage.Weight(),
            ),
#            'var_36 vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(800, 0, 40, name='var_36', label=r'var_36'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_37_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 0.02, name='var_37_leadlep', label=r'var_37_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_37_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 0.02, name='var_37_subleadlep', label=r'var_37_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_37_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 0.02, name='var_37_leadlep', label=r'var_37_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_37_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 0.02, name='var_37_subleadlep', label=r'var_37_subleadlep'),
#                hist.storage.Weight(),
#            ),
#################################################################################################################################################################################
#            'var_38_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 25, name='var_38_leadlep', label=r'var_38_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_38_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 25, name='var_38_subleadlep', label=r'var_38_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_38_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 25, name='var_38_leadlep', label=r'var_38_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_38_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(300, 0, 3000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 25, name='var_38_subleadlep', label=r'var_38_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_39_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_39_leadlep', label=r'var_39_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_39_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_39_subleadlep', label=r'var_39_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_39_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_39_leadlep', label=r'var_39_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_39_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_39_subleadlep', label=r'var_39_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
            'var_40_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 10, name='var_40_leadlep', label=r'var_40_leadlep'),
                hist.storage.Weight(),
            ),
            'var_40_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 10, name='var_40_subleadlep', label=r'var_40_subleadlep'),
                hist.storage.Weight(),
            ),
#            'var_40_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_40_leadlep', label=r'var_40_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_40_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_40_subleadlep', label=r'var_40_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_41_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 20, name='var_41_leadlep', label=r'var_41_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_41_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(400, 0, 20, name='var_41_subleadlep', label=r'var_41_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_41_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(400, 0, 20, name='var_41_leadlep', label=r'var_41_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_41_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(400, 0, 20, name='var_41_subleadlep', label=r'var_41_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
            'var_42_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 15, name='var_42_leadlep', label=r'var_42_leadlep'),
                hist.storage.Weight(),
            ),
            'var_42_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 15, name='var_42_subleadlep', label=r'var_42_subleadlep'),
                hist.storage.Weight(),
            ),
#            'var_42_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(400, 0, 20, name='var_42_leadlep', label=r'var_42_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_42_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(400, 0, 20, name='var_42_subleadlep', label=r'var_42_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_43_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_43_leadlep', label=r'var_43_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_43_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_43_subleadlep', label=r'var_43_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_43_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_43_leadlep', label=r'var_43_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_43_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_43_subleadlep', label=r'var_43_subleadlep'),
#                hist.storage.Weight(),
#            ),
#################################################################################################################################################################################
#            'var_44_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_44_leadlep', label=r'var_44_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_44_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_44_subleadlep', label=r'var_44_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_44_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_44_leadlep', label=r'var_44_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_44_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_44_subleadlep', label=r'var_44_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
            'var_45_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 2, name='var_45_leadlep', label=r'var_45_leadlep'),
                hist.storage.Weight(),
            ),
            'var_45_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 2, name='var_45_subleadlep', label=r'var_45_subleadlep'),
                hist.storage.Weight(),
            ),
#            'var_45_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_45_leadlep', label=r'var_45_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_45_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_45_subleadlep', label=r'var_45_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_46_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_46_leadlep', label=r'var_46_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_46_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(200, 0, 1, name='var_46_subleadlep', label=r'var_46_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_46_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_46_leadlep', label=r'var_46_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_46_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(200, 0, 1, name='var_46_subleadlep', label=r'var_46_subleadlep'),
#                hist.storage.Weight(),
#            ),
#################################################################################################################################################################################
#            'var_47_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5, name='var_47_leadlep', label=r'var_47_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_47_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5, name='var_47_subleadlep', label=r'var_47_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_47_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(1000, 0, 5, name='var_47_leadlep', label=r'var_47_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_47_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(1000, 0, 5, name='var_47_subleadlep', label=r'var_47_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_48_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5, name='var_48_leadlep', label=r'var_48_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_48_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5, name='var_48_subleadlep', label=r'var_48_subleadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_48_leadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(1000, 0, 5, name='var_48_leadlep', label=r'var_48_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_48_subleadlep vs. mass_fourobject': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1600, 0, 8000, name='mass_fourobject', label=r'mass_fourobject [GeV]'),
#                hist.axis.Regular(1000, 0, 5, name='var_48_subleadlep', label=r'var_48_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_49_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 1.8, name='var_49_leadlep', label=r'var_49_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_49_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 1.8, name='var_49_subleadlep', label=r'var_49_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
            'var_50_leadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 4, name='var_50_leadlep', label=r'var_50_leadlep'),
                hist.storage.Weight(),
            ),
            'var_50_subleadlep': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 4, name='var_50_subleadlep', label=r'var_50_subleadlep'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
#            'var_51_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 2, name='var_51_leadlep', label=r'var_51_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_51_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 2, name='var_51_subleadlep', label=r'var_51_subleadlep'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
#            'var_52': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 1.5, name='var_52', label=r'var_52'),
#                hist.storage.Weight(),
#            ),
################################################################################################################################################################################
            'var_53': dah.hist.Hist(
                hist.axis.StrCategory([], name="process", label="Process", growth=True),
                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
                hist.axis.Regular(1000, 0, 2.5, name='var_53', label=r'var_53'),
                hist.storage.Weight(),
            ),
################################################################################################################################################################################
#            'var_54_leadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5, name='var_54_leadlep', label=r'var_54_leadlep'),
#                hist.storage.Weight(),
#            ),
#            'var_54_subleadlep': dah.hist.Hist(
#                hist.axis.StrCategory([], name="process", label="Process", growth=True),
#                hist.axis.StrCategory([], name="region", label="Analysis Region", growth=True),
#                hist.axis.Regular(1000, 0, 5, name='var_54_subleadlep', label=r'var_54_subleadlep'),
#                hist.storage.Weight(),
#            ),

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

        tightElectrons, looseElectrons, tightMuons, looseMuons, AK4Jets, AK8Jets = primed_shift(tightElectrons, looseElectrons, tightMuons, looseMuons, AK4Jets, AK8Jets)

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
            'eejj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'eejj'],
            'mumujj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'mumujj'],
            'emujj_60mll150': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '60mll150', 'emujj'],
            'eejj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'eejj'],
            'mumujj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'mumujj'],
            'emujj_150mll400': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '150mll400', 'emujj'],
            'eejj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'eeTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'eejj'],
            'mumujj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'mumuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'mumujj'],
            'emujj_400mll': ['twoTightLeptons', 'minTwoAK4Jets', 'leadTightLeptonPt60', 'emuTrigger', 'mlljj>800', 'dr>0.4', '400mll', 'emujj'],
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

        print(regions.items())

        for region, cuts in regions.items():
            cut = selections.all(*cuts)

#            output['pt_leadlep'].fill(
#                process=process,
#                region=region,
#                pt_leadlep=tightLeptons[cut][:, 0].pt,
#                weight=weights.weight()[cut],
#            )
#            output['pt_subleadlep'].fill(
#                process=process,
#                region=region,
#                pt_subleadlep=tightLeptons[cut][:, 1].pt,
#                weight=weights.weight()[cut],
#            )
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
#            output['phi_leadlep'].fill(
#                process=process,
#                region=region,
#                phi_leadlep=tightLeptons[cut][:, 0].phi,
#                weight=weights.weight()[cut],
#            )
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
#            output['var_1_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_1_leadlep=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_1_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_1_subleadlep=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_1 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_1=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_1 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_1=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_3_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_3_leadlep=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**(1/3)),
#                weight=weights.weight()[cut],
#            )
#            output['var_3_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_3_subleadlep=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**(1/3)),
#                weight=weights.weight()[cut],
#            )
#            output['var_3 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_3=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**(1/3)),
#                weight=weights.weight()[cut],
#            )
#            output['var_3 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_3=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**(1/3)),
#                weight=weights.weight()[cut],
#            )
#            output['var_4_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_4_leadlep=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_4_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_4_subleadlep=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_4 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_4=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_4 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_4=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)/((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_7_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_7_leadlep=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2/(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_7_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_7_subleadlep=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2/(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_7 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_7=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2/(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_7 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_7=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2/(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_14_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_14_leadlep=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_14_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_14_subleadlep=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_14 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_14=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_14 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_14=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2)**0.5),
#                weight=weights.weight()[cut],
#            )
#            output['var_18_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_18_leadlep=(abs((tightLeptons[cut][:,0].energy)*(tightLeptons[cut][:,0].px)*(tightLeptons[cut][:,0].py)*(tightLeptons[cut][:,0].pz)*(AK4Jets[cut][:,0].energy)*(AK4Jets[cut][:,0].px)*(AK4Jets[cut][:,0].py)*(AK4Jets[cut][:,0].pz)*(AK4Jets[cut][:,1].energy)*(AK4Jets[cut][:,1].px)*(AK4Jets[cut][:,1].py)*(AK4Jets[cut][:,1].pz)))**(1/12),
#                weight=weights.weight()[cut],
#            )
#            output['var_18_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_18_subleadlep=(abs((tightLeptons[cut][:,1].energy)*(tightLeptons[cut][:,1].px)*(tightLeptons[cut][:,1].py)*(tightLeptons[cut][:,1].pz)*(AK4Jets[cut][:,0].energy)*(AK4Jets[cut][:,0].px)*(AK4Jets[cut][:,0].py)*(AK4Jets[cut][:,0].pz)*(AK4Jets[cut][:,1].energy)*(AK4Jets[cut][:,1].px)*(AK4Jets[cut][:,1].py)*(AK4Jets[cut][:,1].pz)))**(1/12),
#                weight=weights.weight()[cut],
#            )
#            output['var_18 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_18=(abs((tightLeptons[cut][:,0].energy)*(tightLeptons[cut][:,0].px)*(tightLeptons[cut][:,0].py)*(tightLeptons[cut][:,0].pz)*(AK4Jets[cut][:,0].energy)*(AK4Jets[cut][:,0].px)*(AK4Jets[cut][:,0].py)*(AK4Jets[cut][:,0].pz)*(AK4Jets[cut][:,1].energy)*(AK4Jets[cut][:,1].px)*(AK4Jets[cut][:,1].py)*(AK4Jets[cut][:,1].pz)))**(1/12),
#                weight=weights.weight()[cut],
#            )
#            output['var_18 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_18=(abs((tightLeptons[cut][:,1].energy)*(tightLeptons[cut][:,1].px)*(tightLeptons[cut][:,1].py)*(tightLeptons[cut][:,1].pz)*(AK4Jets[cut][:,0].energy)*(AK4Jets[cut][:,0].px)*(AK4Jets[cut][:,0].py)*(AK4Jets[cut][:,0].pz)*(AK4Jets[cut][:,1].energy)*(AK4Jets[cut][:,1].px)*(AK4Jets[cut][:,1].py)*(AK4Jets[cut][:,1].pz)))**(1/12),
#                weight=weights.weight()[cut],
#            )
#            output['var_23_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_23_leadlep=((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2)*(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_23_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_23_subleadlep=((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2)*(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_23 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_23=((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2)*(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_23 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_23=((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2)*(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_24_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_24_leadlep=((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2)*(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_24_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_24_subleadlep=((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2)*(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_24 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:, 0]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_24=((((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2)*(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_24 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:, 1]+AK4Jets[cut][:, 0]+AK4Jets[cut][:, 1]).mass,
#                var_24=((((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)**2)*(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)**2+((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz)**2))**0.25,
#                weight=weights.weight()[cut],
#            )
#            output['var_27_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_27_leadlep=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_27_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_27_subleadlep=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_27 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_27=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_27 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_27=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_28_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_28_leadlep=((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_28_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_28_subleadlep=((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_28 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_28=((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_28 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_28=((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass),
#                weight=weights.weight()[cut],
#            )
#            output['var_29_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_29_leadlep=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_29_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_29_subleadlep=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_29 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_29=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_29 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_29=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_30_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_30_leadlep=(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_30_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_30_subleadlep=(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_30 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_30=(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_30 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_30=(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2,
#                weight=weights.weight()[cut],
#            )
#            output['var_31_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_31_leadlep=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_31_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_31_subleadlep=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_31 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_31=((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_31 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_31=((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_32_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_32_leadlep=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.1)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.2),
#                weight=weights.weight()[cut],
#            )
#            output['var_32_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_32_subleadlep=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.1)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.2),
#                weight=weights.weight()[cut],
#            )
#            output['var_32 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_32=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.1)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.2),
#                weight=weights.weight()[cut],
#            )
#            output['var_32 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_32=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.1)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.2),
#                weight=weights.weight()[cut],
#            )
#            output['var_33_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_33_leadlep=(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy)*abs((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).px)*abs((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).py)*abs((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pz))**(-(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass-1200)/(0.2*(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass))**2),
#                weight=weights.weight()[cut],
#            )
#            output['var_33_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_33_subleadlep=0.5*mass_fourobject,
#                weight=weights.weight()[cut],
#            )
#            output['var_33 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_33=(((tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.1)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.2),
#                weight=weights.weight()[cut],
#            )
#            output['var_33 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_33=(((tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.1)/(((tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass)**0.2),
#                weight=weights.weight()[cut],
#            )
#            output['var_34 vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_34=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_34 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_34=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_34 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_34=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_35 vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_35=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]).pt+(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_35 vs. mass_threeobject_leadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_leadlep=(tightLeptons[cut][:,0]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_35=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).pt+(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_35 vs. mass_threeobject_subleadlep'].fill(
#                process=process,
#                region=region,
#                mass_threeobject_subleadlep=(tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_35=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).pt+(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
            output['var_36'].fill(
                process=process,
                region=region,
                var_36=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).mass/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
                weight=weights.weight()[cut],
            )
#            output['var_36 vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_36=(tightLeptons[cut][:, 0]+tightLeptons[cut][:, 1]).mass/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_37_leadlep'].fill(
#                process=process,
#                region=region,
#                var_37_leadlep=tightLeptons[cut][:,0].mass/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['var_37_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_37_subleadlep=tightLeptons[cut][:,1].mass/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['var_37_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_37_leadlep=tightLeptons[cut][:,0].mass/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                weight=weights.weight()[cut],
#            )
#            output['var_37_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_37_subleadlep=tightLeptons[cut][:,1].mass/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                weight=weights.weight()[cut],
#            )
#################################################################################################################################################################################
#            output['var_38_leadlep'].fill(
#                process=process,
#                region=region,
#                var_38_leadlep=tightLeptons[cut][:,0].energy/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_38_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_38_subleadlep=tightLeptons[cut][:,1].energy/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_38_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_38_leadlep=tightLeptons[cut][:,0].energy/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_38_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_38_subleadlep=tightLeptons[cut][:,1].energy/(AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).energy,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_39_leadlep'].fill(
#                process=process,
#                region=region,
#                var_39_leadlep=tightLeptons[cut][:,0].pt/tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_39_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_39_subleadlep=tightLeptons[cut][:,1].pt/tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_39_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_39_leadlep=tightLeptons[cut][:,0].pt/tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_39_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_39_subleadlep=tightLeptons[cut][:,1].pt/tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
            output['var_40_leadlep'].fill(
                process=process,
                region=region,
                var_40_leadlep=tightLeptons[cut][:,0].energy/tightLeptons[cut][:,1].energy,
                weight=weights.weight()[cut],
            )
            output['var_40_subleadlep'].fill(
                process=process,
                region=region,
                var_40_subleadlep=tightLeptons[cut][:,1].energy/tightLeptons[cut][:,0].energy,
                weight=weights.weight()[cut],
            )
#            output['var_40_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_40_leadlep=tightLeptons[cut][:,0].energy/tightLeptons[cut][:,1].energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_40_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_40_subleadlep=tightLeptons[cut][:,1].energy/tightLeptons[cut][:,0].energy,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_41_leadlep'].fill(
#                process=process,
#                region=region,
#                var_41_leadlep=(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_41_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_41_subleadlep=(tightLeptons[cut][:,1].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_41_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_41_leadlep=(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_41_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_41_subleadlep=(tightLeptons[cut][:,1].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
            output['var_42_leadlep'].fill(
                process=process,
                region=region,
                var_42_leadlep=(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,1].energy,
                weight=weights.weight()[cut],
            )
            output['var_42_subleadlep'].fill(
                process=process,
                region=region,
                var_42_subleadlep=(tightLeptons[cut][:,1].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,0].energy,
                weight=weights.weight()[cut],
            )
#            output['var_42_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_42_leadlep=(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,1].energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_42_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_42_subleadlep=(tightLeptons[cut][:,1].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,0].energy,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_43_leadlep'].fill(
#                process=process,
#                region=region,
#                var_43_leadlep=(tightLeptons[cut][:,0].pt-tightLeptons[cut][:,1].pt)/(tightLeptons[cut][:,0].pt+tightLeptons[cut][:,1].pt),
#                weight=weights.weight()[cut],
#            )
#            output['var_43_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_43_subleadlep=(tightLeptons[cut][:,1].pt-tightLeptons[cut][:,0].pt)/(tightLeptons[cut][:,0].pt+tightLeptons[cut][:,1].pt),
#                weight=weights.weight()[cut],
#            )
#            output['var_43_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_43_leadlep=(tightLeptons[cut][:,0].pt-tightLeptons[cut][:,1].pt)/(tightLeptons[cut][:,0].pt+tightLeptons[cut][:,1].pt),
#                weight=weights.weight()[cut],
#            )
#            output['var_43_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_43_subleadlep=(tightLeptons[cut][:,1].pt-tightLeptons[cut][:,0].pt)/(tightLeptons[cut][:,0].pt+tightLeptons[cut][:,1].pt),
#                weight=weights.weight()[cut],
#            )
#################################################################################################################################################################################
#            output['var_44_leadlep'].fill(
#                process=process,
#                region=region,
#                var_44_leadlep=(tightLeptons[cut][:,0].energy-tightLeptons[cut][:,1].energy)/(tightLeptons[cut][:,0].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#            output['var_44_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_44_subleadlep=(tightLeptons[cut][:,1].energy-tightLeptons[cut][:,0].energy)/(tightLeptons[cut][:,0].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#            output['var_44_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_44_leadlep=(tightLeptons[cut][:,0].energy-tightLeptons[cut][:,1].energy)/(tightLeptons[cut][:,0].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#            output['var_44_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_44_subleadlep=(tightLeptons[cut][:,1].energy-tightLeptons[cut][:,0].energy)/(tightLeptons[cut][:,0].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
            output['var_45_leadlep'].fill(
                process=process,
                region=region,
                var_45_leadlep=(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt-tightLeptons[cut][:,1].pt)/(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt+tightLeptons[cut][:,1].pt),
                weight=weights.weight()[cut],
            )
            output['var_45_subleadlep'].fill(
                process=process,
                region=region,
                var_45_subleadlep=(tightLeptons[cut][:,1].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt-tightLeptons[cut][:,0].pt)/(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt+tightLeptons[cut][:,1].pt),
                weight=weights.weight()[cut],
            )
#            output['var_45_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_45_leadlep=(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt-tightLeptons[cut][:,1].pt)/(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt+tightLeptons[cut][:,1].pt),
#                weight=weights.weight()[cut],
#            )
#            output['var_45_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_45_subleadlep=(tightLeptons[cut][:,1].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt-tightLeptons[cut][:,0].pt)/(tightLeptons[cut][:,0].pt+AK4Jets[cut][:,0].pt+AK4Jets[cut][:,1].pt+tightLeptons[cut][:,1].pt),
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_46_leadlep'].fill(
#                process=process,
#                region=region,
#                var_46_leadlep=(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy-tightLeptons[cut][:,1].energy)/(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#            output['var_46_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_46_subleadlep=(tightLeptons[cut][:,1].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy-tightLeptons[cut][:,0].energy)/(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#            output['var_46_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_46_leadlep=(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy-tightLeptons[cut][:,1].energy)/(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#            output['var_46_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_46_subleadlep=(tightLeptons[cut][:,1].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy-tightLeptons[cut][:,0].energy)/(tightLeptons[cut][:,0].energy+AK4Jets[cut][:,0].energy+AK4Jets[cut][:,1].energy+tightLeptons[cut][:,1].energy),
#                weight=weights.weight()[cut],
#            )
#################################################################################################################################################################################
#            output['var_47_leadlep'].fill(
#                process=process,
#                region=region,
#                var_47_leadlep=(tightLeptons[cut][:,0].pt-AK4Jets[cut][:,0].pt-AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_47_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_47_subleadlep=(tightLeptons[cut][:,1].pt-AK4Jets[cut][:,0].pt-AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_47_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_47_leadlep=(tightLeptons[cut][:,0].pt-AK4Jets[cut][:,0].pt-AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_47_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_47_subleadlep=(tightLeptons[cut][:,1].pt-AK4Jets[cut][:,0].pt-AK4Jets[cut][:,1].pt)/tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_48_leadlep'].fill(
#                process=process,
#                region=region,
#                var_48_leadlep=(tightLeptons[cut][:,0].energy-AK4Jets[cut][:,0].energy-AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,1].energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_48_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_48_subleadlep=(tightLeptons[cut][:,1].energy-AK4Jets[cut][:,0].energy-AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,0].energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_48_leadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_48_leadlep=(tightLeptons[cut][:,0].energy-AK4Jets[cut][:,0].energy-AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,1].energy,
#                weight=weights.weight()[cut],
#            )
#            output['var_48_subleadlep vs. mass_fourobject'].fill(
#                process=process,
#                region=region,
#                mass_fourobject=(tightLeptons[cut][:,0]+tightLeptons[cut][:,1]+AK4Jets[cut][:,0]+AK4Jets[cut][:,1]).mass,
#                var_48_subleadlep=(tightLeptons[cut][:,1].energy-AK4Jets[cut][:,0].energy-AK4Jets[cut][:,1].energy)/tightLeptons[cut][:,0].energy,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_49_leadlep'].fill(
#                process=process,
#                region=region,
#                var_49_leadlep = (tightLeptons[cut][:,0] + AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt / tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_49_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_49_subleadlep = (tightLeptons[cut][:,1] + AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt / tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
            output['var_50_leadlep'].fill(
                process=process,
                region=region,
                var_50_leadlep = tightLeptons[cut][:,0].pt / (AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt,
                weight=weights.weight()[cut],
            )
            output['var_50_subleadlep'].fill(
                process=process,
                region=region,
                var_50_subleadlep = tightLeptons[cut][:,1].pt / (AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt,
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
#            output['var_51_leadlep'].fill(
#                process=process,
#                region=region,
#                var_51_leadlep = (AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt / tightLeptons[cut][:,1].pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_51_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_51_subleadlep = (AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt / tightLeptons[cut][:,0].pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
#            output['var_52'].fill(
#                process=process,
#                region=region,
#                var_52 = (tightLeptons[cut][:,0] + tightLeptons[cut][:,1]).pt / (AK4Jets[cut][:,0] + AK4Jets[cut][:,1]).pt,
#                weight=weights.weight()[cut],
#            )
################################################################################################################################################################################
            output['var_53'].fill(
                process=process,
                region=region,
                var_53 = (tightLeptons[cut][:,0].pt + tightLeptons[cut][:,1].pt) / (AK4Jets[cut][:,0].pt + AK4Jets[cut][:,1].pt),
                weight=weights.weight()[cut],
            )
################################################################################################################################################################################
#            output['var_54_leadlep'].fill(
#                process=process,
#                region=region,
#                var_54_leadlep=(tightLeptons[cut][:,0] + AK4Jets[cut][:,0] + AK4Jets[cut][:,1] - tightLeptons[cut][:,1]).pt/(tightLeptons[cut][:,0] + AK4Jets[cut][:,0] + AK4Jets[cut][:,1] + tightLeptons[cut][:,1]).pt,
#                weight=weights.weight()[cut],
#            )
#            output['var_54_subleadlep'].fill(
#                process=process,
#                region=region,
#                var_54_subleadlep=(tightLeptons[cut][:,1] + AK4Jets[cut][:,0] + AK4Jets[cut][:,1] - tightLeptons[cut][:,0]).pt/(tightLeptons[cut][:,1] + AK4Jets[cut][:,0] + AK4Jets[cut][:,1] + tightLeptons[cut][:,0]),
#                weight=weights.weight()[cut],
#            )



        output["weightStats"] = weights.weightStatistics
        return output

    def postprocess(self, accumulator):
        return accumulator

#def selectElectrons(events):
#    # select tight electrons
#    electronSelectTight = (
#            (events.Electron.pt > 53)
#            & (np.abs(events.Electron.eta) < 2.4)
#            & (events.Electron.cutBased_HEEP)
#    )
#
#    # select loose electrons
#    electronSelectLoose = (
#            (events.Electron.pt > 53)
#            & (np.abs(events.Electron.eta) < 2.4)
#            & (events.Electron.cutBased == 2)
#
#    )
#    return events.Electron[electronSelectTight], events.Electron[electronSelectLoose]
#
#def selectMuons(events):
#    # select tight muons
#    muonSelectTight = (
#            (events.Muon.pt > 53)
#            & (np.abs(events.Muon.eta) < 2.4)
#            & (events.Muon.highPtId == 2)
#            & (events.Muon.tkRelIso < 0.1)
#    )
#
#    # select loose muons
#    muonSelectLoose = (
#            (events.Muon.pt > 53) 
#            & (np.abs(events.Muon.eta) < 2.4) 
#            & (events.Muon.highPtId == 2)
#    )
#
#    return events.Muon[muonSelectTight], events.Muon[muonSelectLoose] 
#
#def selectJets(events):
#    # select AK4 jets
#    hem_issue = ((events.Jet.eta <= -3.0) | (events.Jet.eta >= -1.3)) & ((events.Jet.phi <= -1.57) | (events.Jet.phi >= -0.87))
#
#    jetSelectAK4 = (
#            (events.Jet.pt > 40)
#             & (np.abs(events.Jet.eta) < 2.4)
#            & (events.Jet.isTightLeptonVeto)
#            & hem_issue
#    )
#
#    # select AK8 jets (need to add LSF cut)
#    jetSelectAK8 = (
#            (events.FatJet.pt > 200)
#            & (np.abs(events.FatJet.eta) < 2.4)
#            & (events.FatJet.jetId == 2)
#            & (events.FatJet.msoftdrop > 40)
#            & hem_issue
#    )
#
#    return events.Jet[jetSelectAK4], events.FatJet[jetSelectAK8]

######################################################################################################################################################################################

###############################################
# Changing to primed frame
#x' axis is along nonneutrino lepton's momentum
###############################################

def selectElectrons(events):

    print("events.Electron.pt.head(7) preselection --> " + str(events.Electron.pt.head(7)))
    
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

    tightElectrons = events.Electron[electronSelectTight]
    looseElectrons = events.Electron[electronSelectLoose]

    tightElectrons_pt_list = tightElectrons.pt.head(100)

    print("events.Electron.pt.head(50) postselection (tight): ")
    for i in range (0,51):
        print(str(i) + ' --> ' + str(tightElectrons_pt_list[i]))

    print()

    return tightElectrons, looseElectrons

def selectMuons(events):

    print("events.Muon.pt.head(7) preselection --> " + str(events.Muon.pt.head(7)))

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

    tightMuons = events.Muon[muonSelectTight]
    looseMuons = events.Muon[muonSelectLoose]

    tightMuons_pt_list = tightMuons.pt.head(100)

    print("events.Muon.pt.head(50) postselection (tight): ")
    for i in range (0,51):
        print(str(i) + ' --> ' + str(tightMuons_pt_list[i]))

    print()

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

    return events.Jet[jetSelectAK4], events.FatJet[jetSelectAK8]

def primed_shift (tightElectrons, looseElectrons, tightMuons, looseMuons, AK4Jets, AK8Jets):
    #concatenate tightElectrons and tightMuons into tightLeptons and sort by pt 
    tightLeptons = ak.with_name(ak.concatenate((tightElectrons, tightMuons), axis=1), 'PtEtaPhiMCandidate')
    tightLeptons = tightLeptons[ak.argsort(tightLeptons.pt, axis=1, ascending=False)]

    tightLeptons_pt_list = tightLeptons.pt.head(100)

    print("events.Leptons.pt.head(50) postselection (tight): ")
    for i in range (0,51):
        print(str(i) + ' --> ' + str(tightLeptons_pt_list[i]))

    print()

    return tightElectrons, looseElectrons, tightMuons, looseMuons, AK4Jets, AK8Jets



#print('muon.e:')
#print(events.Muon.e.compute())
#print('muon.e length = ' + str(len(events.Muon.e.compute())))
#print('electron.e:')
#print(events.Electron.e.compute())
#print('electron.e length = ' + str(len(events.Electron.e.compute())))
#print('jet.e')
#print(events.Jet.e.compute())
#print('jet.e length = ' + str(len(events.Jet.e.compute())))
