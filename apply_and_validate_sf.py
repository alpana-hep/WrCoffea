#!/usr/bin/env python3
import uproot
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

from hist import Hist
from hist.axis import Variable

# ─── CMS style ────────────────────────────────────────────────────────────────
plt.style.use(hep.style.CMS)

# ─── hard-coded inputs ─────────────────────────────────────────────────────────
dy_file     = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root"
egamma_file = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_EGamma.root"
muon_file   = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_Muon.root"
sf_file     = "mass_dijet_sf.json"
scale       = 59.83e3   # DYJets global factor
# ────────────────────────────────────────────────────────────────────────────────

# load lookup
with open(sf_file) as f:
    lookup  = json.load(f)
edges100  = np.array(lookup["mass_edges"])
sf_EE     = np.array(lookup["sf_EE"])
sf_MM     = np.array(lookup["sf_MM"])

def read_counts(path, region):
    """Return (counts, orig_edges) from the 10 GeV ROOT hist."""
    key = f"{region}/mass_dijet_{region}"
    h   = uproot.open(path)[key]
    return h.to_numpy()  # (counts, edges)

def make_hist(counts, orig_edges, new_edges, weight=1.0):
    """
    Rebin `counts`@`orig_edges` into `new_edges`, then return a hist.Hist.
    """
    centers100 = 0.5 * (new_edges[:-1] + new_edges[1:])
    # rebin by numpy histogram:
    rebinned, _ = np.histogram(
        0.5 * (orig_edges[:-1] + orig_edges[1:]),
        bins=new_edges,
        weights=counts * weight
    )
    # now build a hist.Hist on the 100 GeV axis
    axis100 = Variable(new_edges, name="mass", label=r"$m_{jj}$ [GeV]")
    h100    = Hist(axis100, storage="weight")
    h100.fill(mass=centers100, weight=rebinned)
    return h100

def plot_cr(region, sf, outname, ref_file):
    # read raw
    dy_counts,  orig_edges = read_counts(dy_file,   region)
    ref_counts, _          = read_counts(ref_file, region)

    # make rebinned hist.Hist objects
    h_dy   = make_hist(dy_counts,  orig_edges, edges100, weight=scale)
    h_ref  = make_hist(ref_counts, orig_edges, edges100)
    # apply SF to the DY counts array and build that hist
    dy_rewt = h_dy.values() * sf
    axis100 = Variable(edges100, name="mass", label=r"$m_{jj}$ [GeV]")
    h_rewt  = Hist(axis100, storage="weight")
    centers100 = 0.5 * (edges100[:-1] + edges100[1:])
    h_rewt.fill(mass=centers100, weight=dy_rewt)

    # plot all three
    plt.figure()
    plt.step(
        h_ref.axes["mass"].edges[:-1],
        h_ref.values(), where="post", label="Target Data"
    )
    plt.step(
        h_dy.axes["mass"].edges[:-1],
        h_dy.values(),  where="post", label="DY+Jets"
    )
    plt.step(
        h_rewt.axes["mass"].edges[:-1],
        h_rewt.values(), where="post", label="DY+Jets × SF"
    )
    plt.yscale("log")
    plt.ylim(1, 1e5)
    plt.xlabel(r"$m_{jj}$ [GeV]")
    plt.ylabel("Counts / 100 GeV bin")
    plt.title(region.replace("_", " "))
    plt.legend()
    plt.tight_layout()
    plt.savefig(outname)
    plt.close()

def main():
    plot_cr(
        "WR_EE_Resolved_DYCR", sf_EE, "validation_EE.png", egamma_file
    )
    plot_cr(
        "WR_MuMu_Resolved_DYCR", sf_MM, "validation_MuMu.png", muon_file
    )
    print("Saved plots: validation_EE.png, validation_MuMu.png")

if __name__ == "__main__":
    main()
