from coffea import processor
from coffea.analysis_tools import PackedSelection
import awkward as ak
import numpy as np
import vector
import logging
import warnings

warnings.filterwarnings("ignore", module="coffea.*")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

vector.register_awkward()  # enables Lorentz-vector ops on awkward arrays

# --- Tunables ---
PT_MIN = 20          # strict: pT > 20
ETA_MAX = 2.5
CRACK_START = 1.44   # [1.44, 1.57)
CRACK_END = 1.57
ENDCAP_START = 1.57  # [1.57, 2.5]

# statusFlags bit positions per NanoAOD:
BIT_fromHardProcess = 8
BIT_isLastCopy      = 13

def has_flag(flags, bit):
    # flags: jagged integer array (UShort). Returns boolean jagged array.
    return ((flags >> bit) & 1) == 1

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point=None, sf_file=None):
        self._signal_sample = mass_point  # kept for external compatibility

    def make_output(self):
        return {
            "total_events": 0,
            "region_counts_unweighted":  processor.defaultdict_accumulator(int),  # two_leptons only
            "region_mll80_110_counts":   processor.defaultdict_accumulator(int),  # two_leptons + mll window
            "region_eta157_25_counts":   processor.defaultdict_accumulator(int),  # + eta (1) within mll
            "region_eta_noCrack_counts": processor.defaultdict_accumulator(int),  # + eta (2) within mll
        }

    def process(self, events):
        out = self.make_output()

        # --- Total events in this chunk ---
        out["total_events"] += int(len(events))

        # ---------------- Gen-level DY leptons (Z/γ*) using only GenPart fields ----------------
        gen = events.GenPart

        # pick electrons and muons
        is_lep = (ak.abs(gen.pdgId) == 11) | (ak.abs(gen.pdgId) == 13)
        lep = gen[is_lep]

        # decode statusFlags: last copy & from hard process
        is_last   = has_flag(lep.statusFlags, BIT_isLastCopy)
        from_hard = has_flag(lep.statusFlags, BIT_fromHardProcess)

        # mother check: allow Z (23) OR photon (22) — guard invalid mother index
        mid      = lep.genPartIdxMother              # jagged ints
        has_mom  = mid >= 0
        safe_mid = ak.where(has_mom, mid, 0)         # avoid -1
        mom_pdg  = ak.abs(gen.pdgId[safe_mid])
        from_Zg  = has_mom & ((mom_pdg == 23) | (mom_pdg == 22))

        # keep prompt hard-process leptons, last copy, from Z/γ*
        lepZg = lep[is_last & from_hard & from_Zg]

        # pT > 20 and sort by pT
        lepZg = lepZg[lepZg.pt > PT_MIN]
        lepZg = lepZg[ak.argsort(lepZg.pt, axis=1, ascending=False)]

        # --- Region 1: at least two leptons passing the pT cut ---
        has2 = ak.num(lepZg, axis=1) >= 2
        out["region_counts_unweighted"]["two_leptons"] += int(ak.count_nonzero(has2))

        # Work on the two leading leptons for passing events
        lead2 = lepZg[has2][:, :2]

        # invariant mass via Lorentz vectors built from (pt, eta, phi, mass)
        v0 = vector.awkward.zip({"pt": lead2[:, 0].pt, "eta": lead2[:, 0].eta,
                                 "phi": lead2[:, 0].phi, "mass": lead2[:, 0].mass})
        v1 = vector.awkward.zip({"pt": lead2[:, 1].pt, "eta": lead2[:, 1].eta,
                                 "phi": lead2[:, 1].phi, "mass": lead2[:, 1].mass})
        mll = (v0 + v1).mass
        mll_window_pass = (mll > 80.0) & (mll < 110.0)  # strict: 80 < m_ll < 110

        # --- Re-embed subset masks back to full event length for PackedSelection ---
        counts   = ak.values_astype(has2, np.int64)  # 1 if has2 else 0 per event
        mll_full = ak.fill_none(ak.firsts(ak.unflatten(mll_window_pass, counts)), False)

        # --- Eta helper masks (defined on has2 events) ---
        abs_eta0 = ak.abs(lead2[:, 0].eta)
        abs_eta1 = ak.abs(lead2[:, 1].eta)

        in025_0    = abs_eta0 <= ETA_MAX
        in025_1    = abs_eta1 <= ETA_MAX
        in157_25_0 = (abs_eta0 >= ENDCAP_START) & (abs_eta0 <= ETA_MAX)
        in157_25_1 = (abs_eta1 >= ENDCAP_START) & (abs_eta1 <= ETA_MAX)
        inCrack0   = (abs_eta0 >= CRACK_START) & (abs_eta0 < CRACK_END)
        inCrack1   = (abs_eta1 >= CRACK_START) & (abs_eta1 < CRACK_END)
        noCrack0   = in025_0 & (~inCrack0)
        noCrack1   = in025_1 & (~inCrack1)

        # (1) one lepton in [1.57, 2.5], other in [0, 2.5] but NOT in [1.44, 1.57)
        cond1_pass = (in157_25_0 & noCrack1) | (in157_25_1 & noCrack0)
        # (2) both leptons in [0, 2.5] but NOT in [1.44, 1.57)
        cond2_pass = noCrack0 & noCrack1

        # Re-embed eta conditions back to full event length
        cond1_full = ak.fill_none(ak.firsts(ak.unflatten(cond1_pass, counts)), False)
        cond2_full = ak.fill_none(ak.firsts(ak.unflatten(cond2_pass, counts)), False)

        # --- PackedSelection combining cuts in the requested order ---
        sel = PackedSelection()
        sel.add("two_leptons", has2)
        sel.add("mll_80_110", mll_full)
        sel.add("eta157_25_combo", cond1_full)
        sel.add("eta_noCrack_combo", cond2_full)

        # Counts after pT + two leptons + mll window
        n_mll = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110")))
        out["region_mll80_110_counts"]["two_leptons"] += n_mll

        # Counts within the mll window + eta requirements
        n1 = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110", "eta157_25_combo")))
        n2 = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110", "eta_noCrack_combo")))
        out["region_eta157_25_counts"]["two_leptons"] += n1
        out["region_eta_noCrack_counts"]["two_leptons"] += n2

        return out

    def postprocess(self, accumulator):
        return accumulator
