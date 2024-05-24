import logging
import time
import warnings

import awkward as ak
import dask

from coffea import processor
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess

import utils # contains code for bookkeeping and cosmetics, as well as some boilerplate

warnings.filterwarnings(
    "ignore",
    module="coffea.*"
)

N_FILES_MAX_PER_SAMPLE = 1 # -1 to process all (64M ttbar events takes about 70 minutes)

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        self.myHists = utils.makeHistograms.eventHistos()        

    def process(self, events): #Processes a single NanoEvents chunk
        
        nevts_total = events.metadata["nevts"]
        print(f"Processing {nevts_total} events.")

        events = utils.Objects.createObjects(events)
        selections = utils.Selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events = events[resolved_selections]

        num_selected = ak.num(resolved_events.good_elecs, axis=0).compute()
        
        print(f"{num_selected} events passed the selection ({num_selected/nevts_total*100:.2f}% efficiency).")

        hists = {}
        for mll in ["60mll150", "150mll400", "mll400"]:
           hists[mll] = {}
           mll_selection = selections.all(mll)
           for flavor in ["eejj", "mumujj", "emujj"]:
             hists[mll][flavor] = {}
             flavor_selection = selections.all(flavor)
             selected_events = events[resolved_selections & mll_selection & flavor_selection]
             hists[mll][flavor] = self.myHists.FillHists(selected_events)

        print("Finished processing events and filling histograms.\n")
       
        output = {"nevents": {events.metadata["dataset"]: len(events)}, "hist_dict": hists}

        return output

    def postprocess(self, accumulator):
        return accumulator

def main():
    print("\nStarting analyzer...\n")

    t0 = time.monotonic()

    fileset = utils.file_input.construct_fileset(N_FILES_MAX_PER_SAMPLE)

    # print(f"Fileset: {fileset}\n") for debugging

    print(f"Processes in fileset: {list(fileset.keys())}")
    file_name, file_branch = next(iter(fileset['ttbar__nominal']['files'].items()))
    print(f"\nExample of information in fileset:\n{{\n  'files': {file_name}, ...,")
    print(f"  'metadata': {fileset['ttbar__nominal']['metadata']}\n}}\n")

    NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here

    filemeta, _ = preprocess(fileset, step_size=100_000, skip_bad_files=True)

    to_compute = apply_to_fileset(
        WrAnalysis(),
        max_chunks(filemeta, 300),
        schemaclass=NanoAODSchema,
    )

    all_histograms = to_compute['ttbar__nominal']['hist_dict']

    print("Computing histograms...")
    (out,) = dask.compute(all_histograms)

    print("Histograms computed.\n")
    utils.file_output.save_histograms(out, "example_histos.root")

    exec_time = time.monotonic() - t0
    print(f"\nExecution took {exec_time:.2f} seconds")

if __name__ == "__main__":
    main()
