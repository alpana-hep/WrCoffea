import hist.dask as hda
import awkward as ak

class eventHistos:
    def __init__(self, cuts):
        self.pt_leadlep = hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the leading lepton [GeV]").Weight()
        self.pt_subleadlep = hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the subleading lepton [GeV]").Weight()
        self.pt_leadjet = hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the leading jet [GeV]").Weight()
        self.pt_subleadjet = hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the subleading jet [GeV]").Weight()
        self.eta_leadlep = hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the leading lepton").Weight()
        self.eta_subleadlep = hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the subleading lepton").Weight()
        self.eta_leadjet = hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the leading jet").Weight()
        self.eta_subleadjet = hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the subleading jet").Weight()
        self.phi_leadlep = hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the leading lepton").Weight()
        self.phi_subleadlep = hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the subleading lepton").Weight()
        self.phi_leadjet = hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the leading jet").Weight()
        self.phi_subleadjet = hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the subleading jet").Weight()
        self.mass_dileptons = hda.Hist.new.Reg(1000, 0, 5000, label=r"m_{ll} [GeV]").Weight()
        self.mass_dijets = hda.Hist.new.Reg(1000, 0, 5000, label=r"m_{jj} [GeV]").Weight()
        self.mass_fourobject = hda.Hist.new.Reg(1600, 0, 8000, label=r"m_{lljj} [GeV]").Weight()
        self.cuts = cuts

    def FillHists(self, events, weights):
        self.pt_leadlep.fill(events.leptons[:, 0].pt, weight = weights)
        self.pt_subleadlep.fill(events.leptons[:, 1].pt, weight = weights)
        self.pt_leadjet.fill(events.good_jets[:, 0].pt, weight = weights)
        self.pt_subleadjet.fill(events.good_jets[:, 1].pt, weight = weights)
        self.eta_leadlep.fill(events.leptons[:, 0].eta, weight = weights)
        self.eta_subleadlep.fill(events.leptons[:, 1].eta, weight = weights)
        self.eta_leadjet.fill(events.good_jets[:, 0].eta, weight = weights)
        self.eta_subleadjet.fill(events.good_jets[:, 1].eta, weight = weights)
        self.phi_leadlep.fill(events.leptons[:, 0].phi, weight = weights)
        self.phi_subleadlep.fill(events.leptons[:, 1].phi, weight = weights)
        self.phi_leadjet.fill(events.good_jets[:, 0].phi, weight = weights)
        self.phi_subleadjet.fill(events.good_jets[:, 1].phi, weight = weights)
        self.mass_dileptons.fill((events.leptons[:, 0] + events.leptons[:, 1]).mass, weight = weights)
        self.mass_dijets.fill((events.good_jets[:, 0] + events.good_jets[:, 1]).mass, weight = weights)
        self.mass_fourobject.fill((events.leptons[:, 0] + events.leptons[:, 1] + events.good_jets[:, 0] + events.good_jets[:, 1]).mass, weight = weights)
