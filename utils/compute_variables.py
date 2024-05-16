import awkward as ak

def get_variables(leptons, jets):

    leadlepton_pt = leptons[:,0].pt.compute()
    subleadlepton_pt = leptons[:,1].pt.compute()
    leadjet_pt = jets[:,0].pt.compute()
    subleadjet_pt = jets[:,1].pt.compute()
    leadlepton_eta = leptons[:,0].eta.compute()
    subleadlepton_eta = leptons[:,1].eta.compute()
    leadjet_eta = jets[:,0].eta.compute()
    subleadjet_eta = jets[:,1].eta.compute()
    leadlepton_phi = leptons[:,0].phi.compute()
    subleadlepton_phi = leptons[:,1].phi.compute()
    leadjet_phi = jets[:,0].phi.compute()
    subleadjet_phi = jets[:,1].phi.compute()
    dilepton_mass = (leptons[:, 0] + leptons[:, 1]).mass.compute()
    dijet_mass = (jets[:, 0] + jets[:, 1]).mass.compute()
    fourobject_mass = (leptons[:, 0] + leptons[:, 1] + jets[:, 0] + jets[:, 1]).mass.compute()

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
