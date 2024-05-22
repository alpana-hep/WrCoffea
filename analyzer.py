import time

import awkward as ak
import warnings
from coffea import processor
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
from coffea.analysis_tools import PackedSelection
import copy
import hist
import hist.dask as hda
import dask
import numpy as np
import warnings
from distributed import Client

from utils.file_output import save_histograms
from utils.file_input import construct_fileset
from utils.histos import config
from utils.compute_variables import get_variables
from coffea.dataset_tools import (
    apply_to_fileset,
    max_chunks,
    preprocess,
)
NanoAODSchema.warn_missing_crossrefs = False

warnings.filterwarnings(
    "ignore",
    module="coffea.*"
)
# input files per process, -1 to process all
# 64M ttbar events takes about 45 minutes
N_FILES_MAX_PER_SAMPLE = 1

#client = Client()

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        
        # initialize dictionary of hists for all analysis regions
        self.hist_dict = {}
        for mll in ["60mll150", "150mll400", "mll400"]:
            self.hist_dict[mll] = {}
            for flavor in ["eejj", "mumujj", "emujj"]:
                self.hist_dict[mll][flavor] = {}
                for i in range(len(config["histos"]["HISTO_NAMES"])):
                    #Need to look at hist documentation to improve this
                    self.hist_dict[mll][flavor][config["histos"]["HISTO_NAMES"][i]] =(
                        hda.Hist.new.Reg(bins=config["histos"]["N_BINS"][i],
                                          start=config["histos"]["BIN_LOW"][i],
                                          stop=config["histos"]["BIN_HIGH"][i],
                                          label=config["histos"]["HISTO_LABELS"][i])
                            .Weight()
                    )

    def process(self, events): #Processes a single NanoEvents chunk
   
        # create copies of histogram objects
        hist_dict = copy.deepcopy(self.hist_dict)

        process = events.metadata["process"]  # "ttbar" etc.
        variation = events.metadata["variation"]  # "nominal" etc.

        # normalization for MC
        x_sec = events.metadata["xsec"]
        nevts_total = events.metadata["nevts"]
        lumi = 5974 # /pb for 2018
        xsec_weight = x_sec * lumi / nevts_total

        elecs = events.Electron
        muons = events.Muon
        jets = events.Jet
        
        print(f"Processing {nevts_total} events.")

        # Mask jets and leptons with their individual requirements
        good_elecs = elecs[(elecs.pt > 53) & (np.abs(elecs.eta) < 2.4) & (elecs.cutBased_HEEP)]
        good_muons = muons[(muons.pt > 53) & (np.abs(muons.eta) < 2.4) & (muons.tightId) & (muons.highPtId == 2) & (muons.pfRelIso04_all < 0.1)]
        good_jets = jets[(jets.pt > 40) & (np.abs(jets.eta) < 2.4) & (jets.isTightLeptonVeto)]

        #Require 2 leptons, at least 2 jets, and the pT of the leading lepton > 60
        event_reqs = ((ak.num(good_elecs) + ak.num(good_muons)) == 2) & (ak.num(good_jets)>=2) & ((ak.any(good_elecs.pt > 60, axis=1)) | (ak.any(good_muons.pt > 60, axis=1)))
        event_elecs = good_elecs[event_reqs]
        event_muons = good_muons[event_reqs]
        event_jets = good_jets[event_reqs]

        #Create array of leptons, and order by pT
        leptons = ak.with_name(ak.concatenate((event_elecs, event_muons), axis=1), 'PtEtaPhiMCandidate')
        leptons = leptons[ak.argsort(leptons.pt, axis=1, ascending=False)]

        #Require mlljj > 800
        mlljj_req = (leptons[:, 0] + leptons[:, 1] + event_jets[:, 0] + event_jets[:, 1]).mass > 800
        event_elecs = event_elecs[mlljj_req]
        event_muons = event_muons[mlljj_req]
        event_jets = event_jets[mlljj_req]
        leptons = leptons[mlljj_req]

        #Find min dr value between both jets and both leptons (out of the 4 dr values)
        dr_jl_min = ak.min(event_jets[:,:2].nearest(leptons).delta_r(event_jets[:,:2]), axis=1)

        #Find dr between the leading jet and subleading jet in each event
        dr_j1j2 = event_jets[:,0].delta_r(event_jets[:,1])

        #Find dr between the leading lepton and subleading lepton in each event
        dr_l1l2 = leptons[:,0].delta_r(leptons[:,1])

        #Require that dr > 0.4 between all objects in each event
        dr_reqs = (dr_jl_min  > 0.4) & (dr_j1j2 > 0.4) & (dr_l1l2 > 0.4)
        passing_elecs = event_elecs[dr_reqs]
        passing_muons = event_muons[dr_reqs]
        passing_jets = event_jets[dr_reqs]
        passing_leptons = leptons[dr_reqs]

        num_selected = ak.num(passing_elecs,axis=0).compute()

        print(f"{num_selected} events passed the selection ({num_selected/nevts_total*100:.2f}% efficiency).\n")
         
        mll = (passing_leptons[:, 0] + passing_leptons[:, 1]).mass

        #Define conditions for analysis regions
        selections = PackedSelection(dtype='uint64')
        selections.add_multiple(
            {
                "60mll150": (mll > 60) & (mll < 150),
                "150mll400": (mll > 150) & (mll < 400),
                "mll400": (mll > 400),
                "eejj": (ak.num(passing_elecs) == 2) & (ak.num(passing_muons) == 0),
                "mumujj": (ak.num(passing_elecs) == 0) & (ak.num(passing_muons) == 2),
                "emujj": (ak.num(passing_elecs) == 1) & (ak.num(passing_muons) == 1),
            }
        )

        #Calculate kinematic variables and fill histograms
        for mll in ["60mll150", "150mll400", "mll400"]:
           mll_selection = selections.all(mll)
           for flavor in ["eejj", "mumujj", "emujj"]:
             flavor_selection = selections.all(flavor)
             selected_leptons = passing_leptons[mll_selection & flavor_selection]
             selected_jets = passing_jets[mll_selection & flavor_selection]
             print(f"Filling histograms for events with dilepton mass {mll} and flavor {flavor}.")
             # Creates a list of dask arrays of all kinematic variables
             variables = get_variables(selected_leptons, selected_jets) 
             for i, variable in enumerate(variables):
                # Fill histograms
                hist_dict[mll][flavor][config["histos"]["HISTO_NAMES"][i]].fill(variable)

        print("\nFinished processing events and filling histograms.\n")

        output = {"nevents": {events.metadata["dataset"]: len(events)}, "hist_dict": hist_dict}
        return output

    def postprocess(self, accumulator):
        return accumulator

print("\nStarting analyzer...\n")

t0 = time.monotonic()

fileset = construct_fileset(N_FILES_MAX_PER_SAMPLE)

filemeta, _=preprocess(fileset, step_size=100_000, skip_bad_files=True)

to_compute=apply_to_fileset(
    WrAnalysis(),
    max_chunks(filemeta, 300),
    schemaclass=NanoAODSchema,
    )

all_histograms = to_compute['ttbar__nominal']['hist_dict']

print("Computing histograms...")
(out,) = dask.compute(all_histograms)

print("Histograms computed.\n")
save_histograms(out, "example_histos.root")

exec_time = time.monotonic() - t0
print(f"\nExecution took {exec_time:.2f} seconds")
