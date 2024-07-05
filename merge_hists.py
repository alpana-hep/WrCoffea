import ROOT
import os

# List of input ROOT files
input_files = [
    "root_outputs/hists/2018ULbkg_july/Diboson.root",
    "root_outputs/hists/2018ULbkg_july/Triboson.root",
    "root_outputs/hists/2018ULbkg_july/SingleTop.root",
    "root_outputs/hists/2018ULbkg_july/DYJets.root",
    "root_outputs/hists/2018ULbkg_july/WJets.root",
    "root_outputs/hists/2018ULbkg_july/ttX.root",
    "root_outputs/hists/2018ULbkg_july/tt_semileptonic.root",
    "root_outputs/hists/2018ULbkg_july/tt+tW.root"
]

# Name of the output file
output_file = "root_outputs/hists/2018ULbkg_july/UL18_bkgs.root"

# Create a new ROOT file to store the combined histograms
f_out = ROOT.TFile(output_file, "RECREATE")

# Process each input file
for file_name in input_files:
    # Open the input file
    f_in = ROOT.TFile(file_name, "READ")
    
    # Copy the contents of the input file to the corresponding directory in the output file
    copy_dir(f_in, f_out)
    
    # Close the input file
    f_in.Close()

# Write and close the output file
f_out.Write()
f_out.Close()

print(f"Combined ROOT hists into {output_file}")

# Function to recursively copy directories and their contents
def copy_dir(input_dir, output_dir):
    for key in input_dir.GetListOfKeys():
        obj = key.ReadObj()
        if obj.IsA().InheritsFrom("TDirectory"):
            if not output_dir.GetDirectory(obj.GetName()):
                output_subdir = output_dir.mkdir(obj.GetName())
            else:
                output_subdir = output_dir.GetDirectory(obj.GetName())
            copy_dir(obj, output_subdir)
        else:
            output_dir.cd()
            obj.Write()
