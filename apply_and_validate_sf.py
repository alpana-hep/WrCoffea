#!/usr/bin/env python3
import uproot
import numpy as np
import json
import matplotlib.pyplot as plt
import mplhep as hep               # ← import mplhep

# turn on CMS style globally
plt.style.use(hep.style.CMS)      # ← use the CMS style

# ─── hardcoded inputs ──────────────────────────────────────────────────────────
dy_file     = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_DYJets.root"
egamma_file = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_EGamma.root"
muon_file   = "WR_Plotter/rootfiles/RunII/2018/RunIISummer20UL18/WRAnalyzer_Muon.root"
sf_file     = "mass_dijet_sf.json"
# ────────────────────────────────────────────────────────────────────────────────

# load the JSON lookup
with open(sf_file) as f:
    lookup = json.load(f)
edges   = np.array(lookup["mass_edges"])
sf_EE   = np.array(lookup["sf_EE"])
sf_MM   = np.array(lookup["sf_MM"])

def read_counts(rootfile, region):
    key = f"{region}/mass_dijet_{region}"
    h   = uproot.open(rootfile)[key]
    counts, _ = h.to_numpy()
    return counts

# --- EE control region validation ---
region      = "WR_EE_Resolved_DYCR"
counts_dy   = read_counts(dy_file,   region) * (59.84 * 1000)
counts_tgt  = read_counts(egamma_file, region)
counts_rewt = counts_dy * sf_EE

plt.figure()
plt.step(edges[:-1], counts_tgt,  where="post", label="EGamma (Data)")
plt.step(edges[:-1], counts_dy,   where="post", label="DY+Jets")
plt.step(edges[:-1], counts_rewt, where="post", label="DY+Jets × SF_EE")
plt.yscale("log") 
plt.ylim(0.1, 1e3) # ← set log scale
plt.xlabel(r"$m_{jj}$ [GeV]")
plt.ylabel("Counts per bin")
plt.title("EE control region")
plt.legend()
plt.tight_layout()
plt.savefig("validation_EE.png")
plt.close()

# --- MuMu control region validation ---
region      = "WR_MuMu_Resolved_DYCR"
counts_dy   = read_counts(dy_file, region) * (59.84 * 1000)
counts_tgt  = read_counts(muon_file, region)
counts_rewt = counts_dy * sf_MM

plt.figure()
plt.step(edges[:-1], counts_tgt,  where="post", label="Muon (Data)")
plt.step(edges[:-1], counts_dy,   where="post", label="DY+Jets")
plt.step(edges[:-1], counts_rewt, where="post", label="DYJets × SF_MM")
plt.yscale("log")                                # ← set log scale
plt.ylim(0.1, 1e3)
plt.xlabel(r"$m_{jj}$ [GeV]")
plt.ylabel("Counts per bin")
plt.title("MuMu control region")
plt.legend()
plt.tight_layout()
plt.savefig("validation_MuMu.png")
plt.close()

print("Saved plots: validation_EE.png, validation_MuMu.png")
