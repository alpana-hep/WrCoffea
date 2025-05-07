#!/usr/bin/env python3
import uproot
import json
import numpy as np

# ─── Hardcoded file paths ─────────────────────────────────────────────────────
dy_file     = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root"
egamma_file = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_EGamma.root"
muon_file   = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_Muon.root"
out_file    = "mass_dijet_sf.json"
# ─── Your desired variable bin edges (in GeV) ────────────────────────────────
# here: 0→100,100→200,...,900→1000,1000→1500,1500→2500
new_edges = [0, 100 ,200, 300, 400, 500,600,700,800,900, 1000, 1100, 1200, 1300, 1400, 1500,1750,2000,2500,3000,4000]
# ────────────────────────────────────────────────────────────────────────────────

def derive_sf(dy_path, ref_path, region, edges_out):
    key   = f"{region}/mass_dijet_{region}"
    f_dy  = uproot.open(dy_path)
    f_ref = uproot.open(ref_path)

    # 1) pull out the raw 10 GeV–binned counts + edges
    counts_dy, edges_in  = f_dy[key].to_numpy()
    counts_ref, _        = f_ref[key].to_numpy()

    # 2) apply your global DY scale
    counts_dy *= (59.83 * 1000)

    # 3) compute original bin centers (10 GeV wide)
    centers = 0.5*(edges_in[:-1] + edges_in[1:])

    # 4) rebin onto your variable widths
    dy_rb,  _ = np.histogram(centers, bins=edges_out, weights=counts_dy)
    ref_rb, _ = np.histogram(centers, bins=edges_out, weights=counts_ref)

    # 5) compute **absolute** SF = ref / dy (when both>0), else 1
    sf = np.ones_like(dy_rb, dtype=float)
    mask = (dy_rb>0) & (ref_rb>0)
    sf[mask] = ref_rb[mask] / dy_rb[mask]

    return np.array(edges_out), sf

def main():
    ee_cr = "WR_EE_Resolved_DYCR"
    mm_cr = "WR_MuMu_Resolved_DYCR"

    edges, sf_EE = derive_sf(dy_file,   egamma_file, ee_cr, new_edges)
    _,     sf_MM = derive_sf(dy_file,   muon_file,   mm_cr, new_edges)

    out = {
      "mass_edges": edges.tolist(),
      "sf_EE":      sf_EE.tolist(),
      "sf_MM":      sf_MM.tolist(),
    }
    with open(out_file, "w") as jf:
        json.dump(out, jf, indent=2)

    print(f"Wrote variable‐width SF lookup to {out_file}")

if __name__ == "__main__":
    main()
