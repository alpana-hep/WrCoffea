#!/usr/bin/env python3
import uproot
import numpy as np
import json

# ─── Hardcoded file paths ─────────────────────────────────────────────────────
dy_file     = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root"
egamma_file = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_EGamma.root"
muon_file   = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_Muon.root"
out_file    = "mass_dijet_sf.json"
# ────────────────────────────────────────────────────────────────────────────────

def derive_sf(dy_path, ref_path, region):
    key = f"{region}/mass_dijet_{region}"
    f_dy  = uproot.open(dy_path)
    f_ref = uproot.open(ref_path)
    h_dy  = f_dy[key]
    h_ref = f_ref[key]

    # get your raw DYJets counts + edges
    counts_dy, edges = h_dy.to_numpy()

    # ←――――――――――――――――――――――――――――――――――――――――
    # THIS IS THE ONLY NEW LINE:
    counts_dy = counts_dy * (59.83 * 1000)
    # ―――――――――――――――――――――――――――――――――――――――――→

    # get reference counts
    counts_ref, _ = h_ref.to_numpy()

    # build SF
    sf = np.ones_like(counts_dy, dtype=float)
    mask = (counts_dy > 0) & (counts_ref > 0)

    # normalise to preserve total DY yield (after scaling)
    total_dy  = counts_dy.sum()
    total_ref = counts_ref.sum() if counts_ref.sum() > 0 else 1.0
    norm = total_dy / total_ref

    sf[mask] = (counts_ref[mask] / counts_dy[mask]) * norm

    return edges, sf

def main():
    ee_cr = "WR_EE_Resolved_DYCR"
    mm_cr = "WR_MuMu_Resolved_DYCR"

    edges, sf_EE = derive_sf(dy_file,   egamma_file, ee_cr)
    _,    sf_MM = derive_sf(dy_file,   muon_file,   mm_cr)

    with open(out_file, "w") as jf:
        json.dump({
            "mass_edges": edges.tolist(),
            "sf_EE":      sf_EE.tolist(),
            "sf_MM":      sf_MM.tolist(),
        }, jf, indent=2)

    print(f"Wrote scale‐factor lookup to {out_file}")

if __name__ == "__main__":
    main()
