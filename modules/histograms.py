import hist.dask as dah
import hist

def create_histograms():
    pt_leadlep_axis = hist.axis.Regular(400, 0, 2000, name="pt_leadlep", label=r"p_{T} of the leading lepton [GeV]")
    pt_subleadlep_axis = hist.axis.Regular(400, 0, 2000, name="pt_subleadlep", label=r"p_{T} of the subleading lepton [GeV]")
    pt_leadjet_axis = hist.axis.Regular(400, 0, 2000, name="pt_leadjet", label=r"p_{T} of the leading jet [GeV]")
    pt_subleadjet_axis = hist.axis.Regular(400, 0, 2000, name="pt_subleadjet", label=r"p_{T} of the subleading jet [GeV]")
    pt_dileptons_axis = hist.axis.Regular(200, 0, 1000, name="pt_dileptons", label=r"p^{T}_{ll} [GeV]")

    eta_leadlep_axis = hist.axis.Regular(600, -3, 3, name="eta_leadlep", label=r"#eta of the leading lepton")
    eta_subleadlep_axis = hist.axis.Regular(600, -3, 3, name="eta_subleadlep", label=r"#eta of the subleading lepton")
    eta_leadjet_axis = hist.axis.Regular(600, -3, 3, name="eta_leadjet", label=r"#eta of the leading jet")
    eta_subleadjet_axis = hist.axis.Regular(600, -3, 3, name="eta_subleadjet", label=r"#eta of the subleading jet")

    phi_leadlep_axis = hist.axis.Regular(800, -4, 4, name="phi_leadlep", label=r"#phi of the leading lepton")
    phi_subleadlep_axis = hist.axis.Regular(800, -4, 4, name="phi_subleadlep", label=r"#phi of the subleading lepton")
    phi_leadjet_axis = hist.axis.Regular(800, -4, 4, name="phi_leadjet", label=r"#phi of the leading jet")
    phi_subleadjet_axis = hist.axis.Regular(800, -4, 4, name="phi_subleadjet", label=r"#phi of the subleading jet")

    mass_dileptons_axis = hist.axis.Regular(1000, 0, 5000, name="mass_dileptons", label=r"m_{ll} [GeV]")
    mass_dijets_axis = hist.axis.Regular(1000, 0, 5000, name="mass_dijets", label=r"m_{jj} [GeV]")
    mass_fourobject_axis = hist.axis.Regular(1600, 0, 8000, name="mass_fourobject", label=r"m_{lljj} [GeV]")

    process_axis = hist.axis.StrCategory([], name="process", label="Process", growth=True)
    channel_axis = hist.axis.StrCategory([], name="channel", label="Channel", growth=True)
    mll_axis = hist.axis.StrCategory([], name="mll", label="Dilepton Mass", growth=True)

    hist_dict = {
        "pt_leadlep_h": dah.hist.Hist(pt_leadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_subleadlep_h": dah.hist.Hist(pt_subleadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_leadjet_h": dah.hist.Hist(pt_leadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_subleadjet_h": dah.hist.Hist(pt_subleadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "pt_dileptons_h": dah.hist.Hist(pt_dileptons_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_leadlep_h": dah.hist.Hist(eta_leadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_subleadlep_h": dah.hist.Hist(eta_subleadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_leadjet_h": dah.hist.Hist(eta_leadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "eta_subleadjet_h": dah.hist.Hist(eta_subleadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_leadlep_h": dah.hist.Hist(phi_leadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_subleadlep_h": dah.hist.Hist(phi_subleadlep_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_leadjet_h": dah.hist.Hist(phi_leadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "phi_subleadjet_h": dah.hist.Hist(phi_subleadjet_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "mass_dileptons_h": dah.hist.Hist(mass_dileptons_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "mass_dijets_h": dah.hist.Hist(mass_dijets_axis, process_axis, channel_axis, mll_axis, storage="weight"),
        "mass_fourobject_h": dah.hist.Hist(mass_fourobject_axis, process_axis, channel_axis, mll_axis, storage="weight"),
    }
    
    return hist_dict

def fill_histograms(hist_dict, events, selections, resolved_selections, process, flavor, mass, weights=None):
    for flav in flavor:
        for m in mass:
            cut = resolved_selections & selections.all(flav, m)
#            hist_dict["pt_leadlep_h"].fill(pt_leadlep=events[cut].leptons[:, 0].pt, process=process, channel=flav, mll=m, weight=weights.weight()[cut])
            hist_dict["pt_leadlep_h"].fill(pt_leadlep=events[cut].leptons[:, 0].pt, process=process, channel=flav, mll=m)
            hist_dict["pt_subleadlep_h"].fill(pt_subleadlep=events[cut].leptons[:, 1].pt, process=process, channel=flav, mll=m)
            hist_dict["pt_leadjet_h"].fill(pt_leadjet=events[cut].good_jets[:, 0].pt, process=process, channel=flav, mll=m)
            hist_dict["pt_subleadjet_h"].fill(pt_subleadjet=events[cut].good_jets[:, 1].pt, process=process, channel=flav, mll=m)
            hist_dict["pt_dileptons_h"].fill(pt_dileptons=(events[cut].leptons[:, 0] + events[cut].leptons[:, 1]).pt, process=process, channel=flav, mll=m)
            hist_dict["eta_leadlep_h"].fill(eta_leadlep=events[cut].leptons[:, 0].eta, process=process, channel=flav, mll=m)
            hist_dict["eta_subleadlep_h"].fill(eta_subleadlep=events[cut].leptons[:, 1].eta, process=process, channel=flav, mll=m)
            hist_dict["eta_leadjet_h"].fill(eta_leadjet=events[cut].good_jets[:, 0].eta, process=process, channel=flav, mll=m)
            hist_dict["eta_subleadjet_h"].fill(eta_subleadjet=events[cut].good_jets[:, 1].eta, process=process, channel=flav, mll=m)
            hist_dict["phi_leadlep_h"].fill(phi_leadlep=events[cut].leptons[:, 0].phi, process=process, channel=flav, mll=m)
            hist_dict["phi_subleadlep_h"].fill(phi_subleadlep=events[cut].leptons[:, 1].phi, process=process, channel=flav, mll=m)
            hist_dict["phi_leadjet_h"].fill(phi_leadjet=events[cut].good_jets[:, 0].phi, process=process, channel=flav, mll=m)
            hist_dict["phi_subleadjet_h"].fill(phi_subleadjet=events[cut].good_jets[:, 1].phi, process=process, channel=flav, mll=m)
            hist_dict["mass_dileptons_h"].fill(mass_dileptons=(events[cut].leptons[:, 0] + events[cut].leptons[:, 1]).mass, process=process, channel=flav, mll=m)
            hist_dict["mass_dijets_h"].fill(mass_dijets=(events[cut].good_jets[:, 0] + events[cut].good_jets[:, 1]).mass, process=process, channel=flav, mll=m)

    return hist_dict
