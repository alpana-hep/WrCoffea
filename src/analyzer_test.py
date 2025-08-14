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


class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point, sf_file=None):
        self._signal_sample = mass_point

    def make_output(self):
        return {
            "region_counts_unweighted": processor.defaultdict_accumulator(int),
            "region_eta157_25_counts":   processor.defaultdict_accumulator(int),  # (1)
            "region_eta_noCrack_counts": processor.defaultdict_accumulator(int),  # (2)
        }

    def process(self, events):
        output = self.make_output()

        my_electrons = events.Electron[events.Electron.pt > 19]
        my_muons = events.Muon[events.Muon.pt > 19]

        my_leptons = ak.with_name(ak.concatenate((my_electrons, my_muons), axis=1), 'PtEtaPhiMCandidate')
        my_leptons = ak.pad_none(my_leptons[ak.argsort(my_leptons.pt, axis=1, ascending=False)], 2, axis=1)

        selections = PackedSelection()
        selections.add("two_leptons", (ak.num(my_leptons) >= 2))

        regions = {
            'region': ['two_leptons'],
        }

        # |eta| of the two leading leptons (safe with the two-lepton region mask)
        eta0 = np.abs(my_leptons[:, 0].eta)
        eta1 = np.abs(my_leptons[:, 1].eta)

        # Helper masks
        in025_0    = eta0 <= 2.5
        in025_1    = eta1 <= 2.5
        in157_25_0 = (eta0 >= 1.57) & (eta0 <= 2.5)
        in157_25_1 = (eta1 >= 1.57) & (eta1 <= 2.5)
        inCrack0   = (eta0 >= 1.44) & (eta0 < 1.57)
        inCrack1   = (eta1 >= 1.44) & (eta1 < 1.57)
        noCrack0   = in025_0 & (~inCrack0)
        noCrack1   = in025_1 & (~inCrack1)

        for region, cuts in regions.items():
            cut = selections.all(*cuts)

            # baseline unweighted count
            n_unw = int(ak.sum(cut))
            output["region_counts_unweighted"][region] += n_unw

            # (1) one lepton in [1.57, 2.5], other in [0, 2.5]
            cond1 = ((in157_25_0 & in025_1) | (in157_25_1 & in025_0))
            n1 = int(ak.sum(cut & cond1))
            output["region_eta157_25_counts"][region] += n1

            # (2) one lepton in [0, 2.5] but NOT in [1.44, 1.57), other in [0, 2.5]
            cond2 = ((noCrack0 & in025_1) | (noCrack1 & in025_0))
            n2 = int(ak.sum(cut & cond2))
            output["region_eta_noCrack_counts"][region] += n2

        return output

    def postprocess(self, accumulator):
        return accumulator
