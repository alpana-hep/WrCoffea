def createMasses(mass, resolved_events):

    mass["mlljj_tuple"] = (resolved_events.leptons[:, 0] + resolved_events.leptons[:, 1] + resolved_events.good_jets[:, 0] + resolved_events.good_jets[:, 1]).mass
    mass["mljj_leadLep_tuple"] = (resolved_events.leptons[:, 0] + resolved_events.good_jets[:, 0] + resolved_events.good_jets[:, 1]).mass
    mass["mljj_subleadLep_tuple"] = (resolved_events.leptons[:, 1] + resolved_events.good_jets[:, 0] + resolved_events.good_jets[:, 1]).mass

    return mass
