import ROOT
import matplotlib.pyplot as plt
import os
import numpy as np
import mplhep as hep
import array

hep.style.use("CMS")

# Function to recursively get histograms from a directory in a ROOT file
def get_histograms(directory, path=""):
    histograms = {}
    for key in directory.GetListOfKeys():
        obj = key.ReadObj()
        obj_path = os.path.join(path, obj.GetName())
        if obj.IsA().InheritsFrom("TDirectory"):
            histograms.update(get_histograms(obj, obj_path))
        elif obj.IsA().InheritsFrom("TH1"):
            histograms[obj_path] = obj
    return histograms

def organize_histograms(histograms):
    organized_histograms = {}
    for path, hist in histograms.items():
        components = path.split(os.sep)

        process = components[0]
        channel = components[1]
        mll = components[2]
        hist_name = components[3]

        key = (channel, mll, hist_name)

        if key not in organized_histograms:
            organized_histograms[key] = {}
        organized_histograms[key][process] = hist

    return organized_histograms

def group_histograms(hist_dict):
    stacked_histograms = {}
        
    groupings = {
        'Z+jets': ['DYJets'],
        'tt+tW': ['tt+tW'],
        'Nonprompt': ['tt_semileptonic', 'WJets', 'SingleTop'],
        'Other Backgrounds': ['ttX', 'Diboson', 'Triboson']
    }

    for group_name, processes in groupings.items():
        stacked_histogram = None
        for process in processes:
            if process in hist_dict:
                hist = hist_dict[process]
                if stacked_histogram is None:
                    stacked_histogram = hist.Clone()
                else:
                    stacked_histogram.Add(hist)
        if stacked_histogram is not None:
            stacked_histograms[group_name] = stacked_histogram
    return stacked_histograms

def reorder_dict(mll, original_dict):
    if mll == "60mll150":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'tt+tW', 'Z+jets']
    elif mll == "150mll400":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'tt+tW', 'Z+jets']
    elif mll == "400mll":
        desired_order = ['Other Backgrounds', 'Nonprompt', 'Z+jets', 'tt+tW']
    else:
        return original_dict
    reordered_dict = {key: original_dict[key] for key in desired_order}

    return reordered_dict

def plot_histogram(channel, mll, hist_name, hist_dict):
    fig, ax = plt.subplots()
    ax.text(
        0, 1.05,               
        "Private work (CMS simulation)",              
        fontsize=24,                
        verticalalignment='top',    
        fontproperties="Tex Gyre Heros:italic",
        transform=ax.transAxes
    )

    configurations = {
        "pt_leadlep": {
            "xlabel": "Lead lepton $p_{T}$ (GeV)",
            "60mll150": {"bins": range(0, 1020, 20), "ylabel": "Events / 20 GeV", "xlim": 1e3, "ylim": 6e4},
            "150mll400": {"bins": range(0, 2005, 5), "ylabel": "Events / 5 GeV", "xlim": 2e3, "ylim": 6e4},
            "400mll": {"bins": range(0, 1050, 50), "ylabel": "Events / 50 GeV", "xlim": 1e3, "ylim": 2e3}
        },
        "pt_subleadlep": {
            "xlabel": "Sublead lepton $p_{T}$ (GeV)",
            "60mll150": {"bins": range(0, 520, 20), "ylabel": "Events / 20 GeV", "xlim": 500, "ylim": 2e4},
            "150mll400": {"bins": range(0, 2005, 5), "ylabel": "Events / 5 GeV", "xlim": 2e3, "ylim": 6e4},
            "400mll": {"bins": range(0, 1050, 50), "ylabel": "Events / 50 GeV", "xlim": 1e3, "ylim": 2e3}
        },
        "pt_leadjet": {
            "xlabel": "$p_{T}$ of the leading jet (GeV)",
            "60mll150": {"bins": [0, 40, 100, 200, 400, 600, 800, 1000, 1500, 2000], "ylabel": "Events / 40 GeV", "xlim": 2e3, "ylim": 6e4},
            "150mll400": {"bins": range(0, 2005, 5), "ylabel": "Events / 5 GeV", "xlim": 2e3, "ylim": 6e4},
            "400mll": {"bins": range(0, 2050, 50), "ylabel": "Events / 50 GeV", "xlim": 2e3, "ylim": 6e4}
        }
    }
    if hist_name == "pt_leadlep":
        ax.set_xlabel("Lead lepton $p_{T}$ (GeV)")
        if mll == "60mll150":
            bins = [i for i in range(0, 1020, 20)]
            ax.set_ylabel("Events / 20 GeV")
            ax.set_xlim(0, 1e3)
            ax.set_ylim(1, 6e4)
        elif mll == "150mll400":
            bins = [i for i in range(0, 2005, 5)]
            ax.set_ylabel("Events / 5 GeV")
            ax.set_xlim(0, 2e3)
            ax.set_ylim(1, 6e4)
        elif mll == "400mll":
            bins = [i for i in range(0, 1050, 50)]
            ax.set_ylabel("Events / 50 GeV")
            ax.set_xlim(0, 1e3)
            ax.set_ylim(1e-3, 2e3)
    elif hist_name == "pt_subleadlep":
        ax.set_xlabel("Sublead lepton $p_{T}$ (GeV)")
        if mll == "60mll150":
            bins = [i for i in range(0, 520, 20)]
            ax.set_ylabel("Events / 20 GeV")
            ax.set_xlim(0, 500)
            ax.set_ylim(1, 2e4)
        elif mll == "150mll400":
            bins = [i for i in range(0, 2005, 5)]
            ax.set_ylabel("Events / 5 GeV") 
            ax.set_xlim(0, 2e3)
            ax.set_ylim(1, 6e4)
        elif mll == "400mll":
            bins = [i for i in range(0, 1050, 50)]
            ax.set_ylabel("Events / 50 GeV")
            ax.set_xlim(0, 1e3)
            ax.set_ylim(1e-3, 2e3)
    elif hist_name == "pt_leadjet":
        ax.set_xlabel("$p_{T}$ of the leading jet (GeV)")
        if mll == "60mll150":
            bins = [0,40,100,200,400,600,800,1000,1500,2000]
            ax.set_ylabel("Events / 40 GeV")
            ax.set_xlim(0, 2e3)
            ax.set_ylim(1, 6e4)
        elif mll == "150mll400":
            bins = [i for i in range(0, 2005, 5)]
            ax.set_ylabel("Events / 5 GeV")
            ax.set_xlim(0, 2e3)
            ax.set_ylim(1, 6e4)
        elif mll == "400mll":
            bins = [i for i in range(0, 2050, 50)]
            ax.set_ylabel("Events / 50 GeV")
            ax.set_xlim(0, 2e3)
            ax.set_ylim(1, 6e4)
    elif hist_name == "pt_subleadjet":
        ax.set_xlabel("$p_{T}$ of the subleading jet (GeV)", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(0, 1e3)
        ax.set_ylim(1, 2e4)
        if mll == "60mll150":
            bins = [i for i in range(0, 520, 20)]
        elif mll == "400mll":
            bins = [i for i in range(0, 1050, 50)]
        else:
            bins = [i for i in range(0, 2005, 5)]
    elif hist_name == "pt_dileptons":
        ax.set_xlabel("$p_{T}^{ll}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events / bin", fontsize=20)
        if mll == "60mll150":
            bins = [i for i in range(0, 1050, 50)]
        elif mll == "400mll":
            bins = [i for i in range(0, 1050, 50)]
        else:
            bins = [i for i in range(0, 1050, 50)]
        ax.set_xlim(0, 1e3)
        ax.set_ylim(1e1, 5e6)
    elif hist_name == "pt_dijets":
        ax.set_xlabel("$p_{T}^{jj}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        if mll == "60mll150":
            bins = [i for i in range(0, 520, 20)]
        elif mll == "400mll":
            bins = [i for i in range(0, 1050, 50)]
        else:
            bins = [i for i in range(0, 1050, 50)]
    elif hist_name == "eta_leadlep":
        ax.set_xlabel("$\eta$ of the leading lepton", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(-3, 3)
        ax.set_ylim(1e-3, 5e3)
        bins = [i for i in range(-3, 4, 1)]
    elif hist_name == "eta_subleadlep":
        ax.set_xlabel("$\eta$ of the subleading lepton", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(-3, 3)
        ax.set_ylim(1e-3, 5e3)
        bins = [i for i in range(-3, 4, 1)]
    elif hist_name == "eta_leadjet":
        ax.set_xlabel("$\eta$ of the leading jet", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(-3, 3)
        ax.set_ylim(1e-3, 5e3)
        bins = [i for i in range(-3, 4, 1)]
    elif hist_name == "eta_subleadjet":
        ax.set_xlabel("$\eta$ of the subleading jet", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(-3, 3)
        ax.set_ylim(1e-3, 5e3)
        bins = [i for i in range(-3, 4, 1)]
    elif hist_name == "phi_leadlep":
        ax.set_xlabel("$\phi$ of the leading lepton", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        bins = [i for i in range(-4, 4, 1)]
    elif hist_name == "phi_subleadlep":
        ax.set_xlabel("$\phi$ of the subleading lepton", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        bins = [i for i in range(-4, 4, 1)]
    elif hist_name == "phi_leadjet":
        ax.set_xlabel("$\phi$ of the leading jet", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        bins = [i for i in range(-4, 4, 1)]
    elif hist_name == "phi_subleadjet":
        ax.set_xlabel("$phi$ of the subleading jet", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        bins = [i for i in range(-4, 4, 1)]
    elif hist_name == "mass_dileptons":
        ax.set_xlabel("$m_{ll}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(0, 1e3)
        ax.set_ylim(1, 5e6)
        bins = [i for i in range(0, 1050, 50)]
    elif hist_name == "mass_dijets":
        ax.set_xlabel("$m_{jj}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(800, 8000)
        ax.set_ylim(1e-3, 2e4)
        bins = [i for i in range(0, 1050, 50)]
    elif hist_name == "mass_threeobject_leadlep":
        ax.set_xlabel("$m_{ljj}^{lead lep}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(800, 8000)
        ax.set_ylim(1e-3, 2e4)
        if mll == "60mll150":
            bins = [800,1000,1200,1400,1600,2000,2400,2800,3200,8000]
        elif mll == "400mll":
            bins = [i for i in range(800, 8020, 20)]
        else:
            bins = [i for i in range(800, 8020, 20)]
    elif hist_name == "mass_threeobject_subleadlep":
        ax.set_xlabel("$m_{ljj}^{sublead lep}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events", fontsize=20)
        ax.set_xlim(800, 8000)
        ax.set_ylim(1e-3, 2e4)
        if mll == "60mll150":
            bins = [800,1000,1200,1400,1600,2000,2400,2800,3200,8000]
        elif mll == "400mll":
            bins = [i for i in range(800, 8020, 20)]
        else:
            bins = [i for i in range(800, 8020, 20)]
    elif hist_name == "mass_fourobject":
        ax.set_xlabel("$m_{lljj}$ (GeV)", fontsize=20)
        ax.set_ylabel("Events / bin", fontsize=20)
        ax.set_xlim(800, 8000)
        ax.set_ylim(1, 9e3)
        if mll == "60mll150":
            bins = [800,1000,1200,1400,1600,2000,2400,2800,3200,8000]
        elif mll == "400mll":
            ax.set_ylim(1, 9e3)
            bins = [800,1000,1200,1400,1600,2000,2400,2800,3200,8000]
        else:
            bins = [800,1000,1200,1400,1600,2000,2400,2800,3200,8000]

    bins = array.array('d', bins)
    # Initialize variables to hold histogram data
    hist_data = []
    labels = []

    # Define colors for each histogram stack
    colors = {
        'Z+jets': '#FFFF00',
        'tt+tW': '#FF0000',
        'Nonprompt': '#32CD32',
        'Other Backgrounds': '#00BFFF'
    }

    for process, hist in hist_dict.items():

        rebinned_hist = hist.Rebin(len(bins)-1, "hnew", bins)
        
        hist_contents = []
        for bin in range(1, rebinned_hist.GetNbinsX() + 1):
            bin_width = bins[bin] - bins[bin - 1]
#            print(bin_width)
            hist_contents.append(rebinned_hist.GetBinContent(bin) * 59.74 * 1000)

        hist_data.append(hist_contents)
        labels.append(process)

    # Plot stacked histogram
    hep.histplot(
            hist_data,
            bins,
            stack=True,
            histtype='fill',
            label=labels,
            color=[colors[process] for process in labels],
            ax=ax
    )

    # Options common to all plots
    ax.set_yscale('log')

    # Set plot labels and title
    plt.legend()
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles[::-1], labels[::-1])
#    hep.cms.label(data=False, lumi=59.74, fontsize=17)

    # Create output directory if it doesn't exist
    output_path = os.path.join("plots", channel, mll,  f"{hist_name}.png")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Save the plot
    plt.savefig(output_path)
    plt.close()


input_file = "root_outputs/hists/2018ULbkg_triggers_hem/UL18_bkgs.root"
f_in = ROOT.TFile(input_file, "READ")

my_histos = get_histograms(f_in)

sorted_histograms = organize_histograms(my_histos)

for (channel, mll, hist_name), hist_dict in sorted_histograms.items():
    grouped_hist_dict = group_histograms(hist_dict)
    reordered_dict = reorder_dict(mll, grouped_hist_dict)
    plot_histogram(channel, mll, hist_name, reordered_dict)
    print(f"Saved plots/{channel}/{mll}/{hist_name}.png")

f_in.Close()

print(f"Finished making histograms.")

