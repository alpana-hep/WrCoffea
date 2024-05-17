import awkward as ak

def get_variables(leptons, jets):

    leadlepton_pt = leptons[:,0].pt
    subleadlepton_pt = leptons[:,1].pt
    leadjet_pt = jets[:,0].pt
    subleadjet_pt = jets[:,1].pt
    leadlepton_eta = leptons[:,0].eta
    subleadlepton_eta = leptons[:,1].eta
    leadjet_eta = jets[:,0].eta
    subleadjet_eta = jets[:,1].eta
    leadlepton_phi = leptons[:,0].phi
    subleadlepton_phi = leptons[:,1].phi
    leadjet_phi = jets[:,0].phi
    subleadjet_phi = jets[:,1].phi
    dilepton_mass = (leptons[:, 0] + leptons[:, 1]).mass
    dijet_mass = (jets[:, 0] + jets[:, 1]).mass
    fourobject_mass = (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass

    variables = [leadlepton_pt,
                subleadlepton_pt,
                leadjet_pt,
                subleadjet_pt,
                leadlepton_eta,
                subleadlepton_eta,
                leadjet_eta,
                subleadjet_eta,
                leadlepton_phi,
                subleadlepton_phi,
                leadjet_phi,
                subleadjet_phi,
                dilepton_mass,
                dijet_mass,
                fourobject_mass,
                ]

    return variables
