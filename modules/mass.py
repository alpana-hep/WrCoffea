def createMasses(hists, resolved_events):

    hists["mlljj_vals"] = (resolved_events.leptons[:, 0] + resolved_events.leptons[:, 1] + resolved_events.good_jets[:, 0] + resolved_events.good_jets[:, 1]).mass
    hists["mljj_leadLep_vals"] = (resolved_events.leptons[:, 0] + resolved_events.good_jets[:, 0] + resolved_events.good_jets[:, 1]).mass
    hists["mljj_subleadLep_vals"] = (resolved_events.leptons[:, 1] + resolved_events.good_jets[:, 0] + resolved_events.good_jets[:, 1]).mass

    return hists
