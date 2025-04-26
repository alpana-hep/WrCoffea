#!/usr/bin/env python3
import json
import numpy as np
import matplotlib.pyplot as plt
import mplhep as hep

plt.style.use(hep.style.CMS)

# ─── Load your JSON lookup ─────────────────────────────────────────────────────
with open("mass_dijet_sf.json") as f:
    lookup = json.load(f)

edges = np.array(lookup["mass_edges"])     # length N+1
sf_EE = np.array(lookup["sf_EE"])          # length N
sf_MM = np.array(lookup["sf_MM"])          # length N

# Define a “nominal” SF as the average of EE and MuMu (or choose your own)
sf_nominal = 0.5 * (sf_EE + sf_MM)

# bin centers for plotting
centers = 0.5 * (edges[:-1] + edges[1:])

# ─── Make the plot ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots()

# 1) Nominal ratio with markers
ax.errorbar(
    centers, sf_nominal, 
    yerr=None,        # if you have uncertainties you can put them here
    color="black", 
    label="Nominal SF",
    fmt='none',
    xerr=True
)

# 2) EE‐only and μμ‐only as step histograms
ax.step(edges[:-1], sf_EE,   where="post", color="green", label="EE‐only SF")
ax.step(edges[:-1], sf_MM,   where="post", color="blue",  label="μμ‐only SF")

# axes labels & limits
ax.set_xlabel(r"$m_{jj}$ [GeV]")
ax.set_ylabel("Scale factor (Data / DY)")
ax.set_xlim(edges[0], edges[-1])
ax.set_ylim(0.0, max(sf_nominal.max(), sf_EE.max(), sf_MM.max())*1.5)

# legend
ax.legend(loc="upper right", frameon=False)

# CMS label & lumi text
hep.cms.text("Work in Progress", loc=0, ax=ax)
hep.cms.lumitext("59.84 fb$^{-1}$ (13 TeV)", ax=ax)

plt.tight_layout()
plt.savefig("mass_sf_ratio.png")
plt.close(fig)

print("Saved mass_sf_ratio.png")
