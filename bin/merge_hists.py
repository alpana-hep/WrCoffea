import ROOT
import os
import argparse

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

parser = argparse.ArgumentParser(description="Combine ROOT histograms from multiple files into a single file.")
parser.add_argument("input_directory", type=str, help="Directory containing the input ROOT files.")
parser.add_argument("output_file", type=str, help="Name of the output ROOT file.")
args = parser.parse_args()

#required_files = [
#    "DYJets.root", "tt+tW.root", "WJets.root", "tt_semileptonic.root",
#    "Diboson.root", "Triboson.root", "ttX.root", "SingleTop.root"
#]

required_files = ["MWR1600_MN800_newest.root", "MWR2000_MN1000_newest.root", "MWR2400_MN1200_newest.root", "MWR2800_MN1400_newest.root", "MWR3200_MN1600_newest.root"]

input_files = [os.path.join(args.input_directory, f) for f in required_files if os.path.isfile(os.path.join(args.input_directory, f))]

output_file = f"{args.input_directory}/{args.output_file}"

f_out = ROOT.TFile(output_file, "RECREATE")

for file_name in input_files:
    f_in = ROOT.TFile(file_name, "READ")
    copy_dir(f_in, f_out)
    f_in.Close()

f_out.Write()
f_out.Close()

print(f"Combined ROOT hists into {output_file}")

# Example usage
# python3 merge_hists.py root_outputs/hists/2018ULbkg_triggers_hem UL18_bkgs.root
