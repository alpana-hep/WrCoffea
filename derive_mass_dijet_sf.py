#!/usr/bin/env python3
import uproot
import json
import numpy as np
from hist import Hist
from hist.axis import Variable

# ─── Hardcoded file paths ─────────────────────────────────────────────────────
dy_file     = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root"
egamma_file = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_EGamma.root"
muon_file   = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_Muon.root"
out_file    = "mass_dijet_sf.json"
# ────────────────────────────────────────────────────────────────────────────────

def derive_sf(dy_path, ref_path, region):
    key   = f"{region}/mass_dijet_{region}"
    f_dy  = uproot.open(dy_path)
    f_ref = uproot.open(ref_path)

    # get the raw 10 GeV–binned counts + edges
    counts_dy, edges  = f_dy[key].to_numpy()
    counts_ref, _     = f_ref[key].to_numpy()

    # scale DYJets by your global factor
    counts_dy *= (59.83 * 1000)

    # build hist.Hist on the original edges
    axis = Variable(edges, name="mass", label=r"$m_{jj}$ [GeV]")
    hdy  = Hist(axis, storage="weight")
    href = Hist(axis, storage="weight")

    # fill each bin‐center with its count
    centers = 0.5 * (edges[:-1] + edges[1:])
    hdy .fill(mass=centers, weight=counts_dy)
    href.fill(mass=centers, weight=counts_ref)

    # rebin by merging 5×10 GeV→50 GeV if you want 50 GeV bins (or 10 for 100 GeV)
    # here I keep your 5→1 factor
    hdy_rb  = hdy[::(10 * 1j)]
    href_rb = href[::(10 * 1j)]

    # extract the rebinned counts & edges
    dy_rb     = hdy_rb .values()
    ref_rb    = href_rb.values()
    edges_new = hdy_rb.axes["mass"].edges

    # compute absolute SF = ref / dy (when both >0), else 1
    sf = np.ones_like(dy_rb, dtype=float)
    mask = (dy_rb > 0) & (ref_rb > 0)
    sf[mask] = ref_rb[mask] / dy_rb[mask]

    return edges_new, sf

def main():
    ee_cr = "WR_EE_Resolved_DYCR"
    mm_cr = "WR_MuMu_Resolved_DYCR"

    edges, sf_EE = derive_sf(dy_file,   egamma_file, ee_cr)
    _,     sf_MM = derive_sf(dy_file,   muon_file,   mm_cr)

    out = {
        "mass_edges": edges.tolist(),
        "sf_EE":      sf_EE.tolist(),
        "sf_MM":      sf_MM.tolist(),
    }
    with open(out_file, "w") as jf:
        json.dump(out, jf, indent=2)

    print(f"Wrote 100 GeV–binned SF lookup to {out_file}")

if __name__ == "__main__":
    main()
