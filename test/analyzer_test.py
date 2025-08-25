from coffea import processor
from coffea.analysis_tools import PackedSelection
import awkward as ak
import numpy as np
import logging
import warnings

warnings.filterwarnings("ignore", module="coffea.*")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Tunables ---
PT_MIN = 19          # strict: pT > 20 (PT_MIN=19 implies >19 -> effectively >20 for ints)
ETA_MAX = 2.5
CRACK_START = 1.44   # barrel/crack boundary (exclude [1.44,1.57))
CRACK_END = 1.57
ENDCAP_START = 1.57  # endcap start

class WrAnalysis(processor.ProcessorABC):
    def __init__(self, mass_point=None, sf_file=None):
        self._signal_sample = mass_point  # kept for external compatibility

    def make_output(self):
        return {
            "total_events": 0,
            # after ≥2 leptons (pT cut only)
            "region_counts_unweighted":  processor.defaultdict_accumulator(int),
            # after ≥2 leptons + 80 < mll < 110
            "region_mll80_110_counts":   processor.defaultdict_accumulator(int),
            # new splits inside mll window
            "region_barrel_endcap_counts": processor.defaultdict_accumulator(int),
            "region_both_endcap_counts":   processor.defaultdict_accumulator(int),
            "region_both_barrel_counts":   processor.defaultdict_accumulator(int),
            # (kept) both leptons in [0,2.5] but NOT in crack
            "region_eta_noCrack_counts": processor.defaultdict_accumulator(int),
        }

    def process(self, events):
        out = self.make_output()

        # --- Total events in this chunk ---
        out["total_events"] += int(len(events))

        # --- pT selections & sorting by pT ---
        ele = events.Electron[events.Electron.pt > PT_MIN]
        mu  = events.Muon[events.Muon.pt > PT_MIN]

        # concatenate & sort; keep four-vector behavior for (l0+l1).mass
        leptons = ak.with_name(ak.concatenate([ele, mu], axis=1), "PtEtaPhiMCandidate")
        leptons = leptons[ak.argsort(leptons.pt, axis=1, ascending=False)]

        # --- Region base: at least two leptons passing pT cut ---
        has2 = ak.num(leptons, axis=1) >= 2
        out["region_counts_unweighted"]["two_leptons"] += int(ak.count_nonzero(has2))

        # Work on the two leading leptons for passing events
        lead2 = leptons[has2][:, :2]

        # absolute etas
        abs_eta0 = np.abs(lead2[:, 0].eta)
        abs_eta1 = np.abs(lead2[:, 1].eta)

        # dilepton mass window (80,110)
        mll = (lead2[:, 0] + lead2[:, 1]).mass
        mll_window_pass = (mll > 80.0) & (mll < 110.0)

        # Re-embed per-has2 masks back to full event length for PackedSelection
        counts = ak.values_astype(has2, np.int64)
        def _to_full(mask_on_has2):
            return ak.fill_none(ak.firsts(ak.unflatten(mask_on_has2, counts)), False)

        mll_full = _to_full(mll_window_pass)

        # --- Helper eta regions on the two leading leptons ---
        in_barrel_0 = (abs_eta0 <= CRACK_START)                 # [0,1.44]
        in_barrel_1 = (abs_eta1 <= CRACK_START)

        in_endcap_0 = (abs_eta0 >= ENDCAP_START) & (abs_eta0 <= ETA_MAX)  # [1.57,2.5]
        in_endcap_1 = (abs_eta1 >= ENDCAP_START) & (abs_eta1 <= ETA_MAX)

        in_crack_0  = (abs_eta0 >= CRACK_START) & (abs_eta0 < CRACK_END)  # [1.44,1.57)
        in_crack_1  = (abs_eta1 >= CRACK_START) & (abs_eta1 < CRACK_END)

        in_025_0 = (abs_eta0 <= ETA_MAX)
        in_025_1 = (abs_eta1 <= ETA_MAX)

        no_crack_0 = in_025_0 & (~in_crack_0)
        no_crack_1 = in_025_1 & (~in_crack_1)

        # --- Categories ---
        cond_barrel_endcap = (in_barrel_0 & in_endcap_1) | (in_barrel_1 & in_endcap_0)
        cond_both_endcap   = in_endcap_0 & in_endcap_1
        cond_both_barrel   = in_barrel_0 & in_barrel_1
        cond_no_crack_both = no_crack_0 & no_crack_1

        # Re-embed to full event length
        cond_barrel_endcap_full = _to_full(cond_barrel_endcap)
        cond_both_endcap_full   = _to_full(cond_both_endcap)
        cond_both_barrel_full   = _to_full(cond_both_barrel)
        cond_no_crack_full      = _to_full(cond_no_crack_both)

        # --- PackedSelection with explicit steps ---
        sel = PackedSelection()
        sel.add("two_leptons", has2)
        sel.add("mll_80_110", mll_full)
        sel.add("barrel_endcap", cond_barrel_endcap_full)
        sel.add("both_endcap",   cond_both_endcap_full)
        sel.add("both_barrel",   cond_both_barrel_full)
        sel.add("eta_noCrack_combo", cond_no_crack_full)

        # after pT + two leptons + mll window
        n_mll = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110")))
        out["region_mll80_110_counts"]["two_leptons"] += n_mll

        # within mll window: requested categories
        n_barrel_endcap = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110", "barrel_endcap")))
        n_both_endcap   = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110", "both_endcap")))
        n_both_barrel   = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110", "both_barrel")))

        out["region_barrel_endcap_counts"]["two_leptons"] += n_barrel_endcap
        out["region_both_endcap_counts"]["two_leptons"]   += n_both_endcap
        out["region_both_barrel_counts"]["two_leptons"]   += n_both_barrel

        # (optional/kept) within mll window: both leptons in [0,2.5] and not in crack
        n_no_crack = int(ak.count_nonzero(sel.all("two_leptons", "mll_80_110", "eta_noCrack_combo")))
        out["region_eta_noCrack_counts"]["two_leptons"] += n_no_crack

        return out

    def postprocess(self, accumulator):
        return accumulator
