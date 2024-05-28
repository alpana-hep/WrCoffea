from coffea.nanoevents import NanoAODSchema
import argparse
import time
import utils
from coffea.dataset_tools import apply_to_fileset, max_chunks, preprocess
from analyzer import WrAnalysis

NanoAODSchema.warn_missing_crossrefs = False  # silences warnings about branches we will not use here

def main(N_FILES_MAX_PER_SAMPLE, output_file):

    print("\nStarting analyzer...\n")

    t0 = time.monotonic()

    #Preprocess files (get steps sizes etc)
    fileset = utils.file_input.construct_fileset(N_FILES_MAX_PER_SAMPLE)
    print(f"fileset: {fileset}\n")
    filemeta, _ = preprocess(fileset, step_size=100_000, skip_bad_files=True)
    print(f"Preprocessed files: {filemeta}\n")

    #Process files
    to_compute = apply_to_fileset(
        data_manipulation=WrAnalysis(),
        fileset=filemeta,
        schemaclass=NanoAODSchema,
    )
    print("Finished processing events and filling histograms.\n")

    #Get histograms
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
