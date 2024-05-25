import logging
import time
import warnings
import argparse
import uproot
import awkward as ak

from coffea import processor
from coffea.nanoevents import NanoAODSchema
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess

import utils # contains code for bookkeeping and cosmetics, as well as some boilerplate

warnings.filterwarnings(
    "ignore",
    module="coffea.*"
)

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        self.eejj_60mll150 = utils.makeHistograms.eventHistos(['eejj', '60mll150'])
        self.mumujj_60mll150 = utils.makeHistograms.eventHistos(['mumujj', '60mll150'])
        self.emujj_60mll150 = utils.makeHistograms.eventHistos(['emujj', '60mll150'])

        self.eejj_150mll400 = utils.makeHistograms.eventHistos(['eejj','150mll400'])
        self.mumujj_150mll400 = utils.makeHistograms.eventHistos(['mumujj','150mll400'])
        self.emujj_150mll400 = utils.makeHistograms.eventHistos(['emujj','150mll400'])

        self.eejj_400mll = utils.makeHistograms.eventHistos(['eejj','400mll'])
        self.mumujj_400mll = utils.makeHistograms.eventHistos(['mumujj','400mll'])
        self.emujj_400mll = utils.makeHistograms.eventHistos(['emujj','400mll'])

        self.hists = {
            "eejj_60mll150": self.eejj_60mll150,
            "mumujj_60mll150": self.mumujj_60mll150,
            "emujj_60mll150": self.emujj_60mll150,
            "eejj_150mll400": self.eejj_150mll400,
            "mumujj_150mll400": self.mumujj_150mll400,
            "emujj_150mll400": self.emujj_150mll400,
            "eejj_400mll": self.eejj_400mll,
            "mumujj_400mll": self.mumujj_400mll,
            "emujj_400mll": self.emujj_400mll
        }

    def process(self, events): #Processes a single NanoEvents chunk

        nevts = events.metadata["nevts"]
        print(f"Processing {nevts} events.")

        events = utils.Objects.createObjects(events)
        selections = utils.Selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")

        for hist_name, hist_obj in self.hists.items():
            hist_obj.FillHists(events[resolved_selections & selections.all(*hist_obj.cuts)])

        return {"nevents": {events.metadata["dataset"]: len(events)}, "hist_dict": self.hists}

    def postprocess(self, accumulator):
        return accumulator

def main(N_FILES_MAX_PER_SAMPLE, output_file):

    print("\nStarting analyzer...\n")

    t0 = time.monotonic()

    fileset = utils.file_input.construct_fileset(N_FILES_MAX_PER_SAMPLE)

    print(f"Processes in fileset: {list(fileset.keys())}")
    file_name, file_branch = next(iter(fileset['2018UL__TTTo2L2Nu']['files'].items()))
    print(f"\nExample of information in fileset:\n{{\n  'files': {file_name}, ...,")
    print(f"  'metadata': {fileset['2018UL__TTTo2L2Nu']['metadata']}\n}}\n")

    NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here

    filemeta, _ = preprocess(fileset, step_size=100_000, skip_bad_files=True)

    to_compute = apply_to_fileset(
        WrAnalysis(),
        max_chunks(filemeta, 300),
        schemaclass=NanoAODSchema,
    )

    print("Finished processing events and filling histograms.\n")

    all_histograms = to_compute['2018UL__TTTo2L2Nu']['hist_dict']

    utils.file_output.save_histograms(all_histograms, output_file)

    exec_time = time.monotonic() - t0
    print(f"Execution took {exec_time:.2f} seconds")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the analyzer and save histograms to a specified ROOT file.")
    parser.add_argument("--nFiles", type=int, default=1, help="Number of files to analyze (-1 for all).")
    parser.add_argument("--outputFile", type=str, default="example_hists.root", help="Name of the output ROOT histogram file.")
    args = parser.parse_args()

    main(args.nFiles, args.outputFile)
