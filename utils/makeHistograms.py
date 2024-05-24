import hist.dask as hda
import awkward as ak

class eventHistos:
    def __init__(self):
        self.hist_dict_template = {
            "pt_leadlep": hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the leading lepton [GeV]").Weight(),
            "pt_subleadlep": hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the subleading lepton [GeV]").Weight(),
            "pt_leadjet": hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the leading jet [GeV]").Weight(),
            "pt_subleadjet": hda.Hist.new.Reg(400, 0, 2000, label=r"p_{T} of the subleading jet [GeV]").Weight(),
            "eta_leadlep": hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the leading lepton").Weight(),
            "eta_subleadlep": hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the subleading lepton").Weight(),
            "eta_leadjet": hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the leading jet").Weight(),
            "eta_subleadjet": hda.Hist.new.Reg(600, -3, 3, label=r"#eta of the subleading jet").Weight(),
            "phi_leadlep": hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the leading lepton").Weight(),
            "phi_subleadlep": hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the subleading lepton").Weight(),
            "phi_leadjet": hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the leading jet").Weight(),
            "phi_subleadjet": hda.Hist.new.Reg(800, -4, 4, label=r"#phi of the subleading jet").Weight(),
            "mass_dileptons": hda.Hist.new.Reg(1000, 0, 5000, label=r"m_{ll} [GeV]").Weight(),
            "mass_dijets": hda.Hist.new.Reg(1000, 0, 5000, label=r"m_{jj} [GeV]").Weight(),
            "mass_fourobject": hda.Hist.new.Reg(1600, 0, 8000, label=r"m_{lljj} [GeV]").Weight()
        }

    def FillHists(self, events):
        hist_dict = {}
        for hist_name, hist_template in self.hist_dict_template.items():
            hist_dict[hist_name] = hist_template.copy()  # Create a copy of the template for each histogram

        # Fill histograms
        hist_dict["pt_leadlep"].fill(events.leptons[:, 0].pt)
        hist_dict["pt_subleadlep"].fill(events.leptons[:, 1].pt)
        hist_dict["pt_leadjet"].fill(events.good_jets[:, 0].pt)
        hist_dict["pt_subleadjet"].fill(events.good_jets[:, 1].pt)
        hist_dict["eta_leadlep"].fill(events.leptons[:, 0].eta)
        hist_dict["eta_subleadlep"].fill(events.leptons[:, 1].eta)
        hist_dict["eta_leadjet"].fill(events.good_jets[:, 0].eta)
        hist_dict["eta_subleadjet"].fill(events.good_jets[:, 1].eta)
        hist_dict["phi_leadlep"].fill(events.leptons[:, 0].phi)
        hist_dict["phi_subleadlep"].fill(events.leptons[:, 1].phi)
        hist_dict["phi_leadjet"].fill(events.good_jets[:, 0].phi)
        hist_dict["phi_subleadjet"].fill(events.good_jets[:, 1].phi)
        hist_dict["mass_dileptons"].fill((events.leptons[:, 0] + events.leptons[:, 1]).mass)
        hist_dict["mass_dijets"].fill((events.good_jets[:, 0] + events.good_jets[:, 1]).mass)
        hist_dict["mass_fourobject"].fill((events.leptons[:, 0] + events.leptons[:, 1] + events.good_jets[:, 0] + events.good_jets[:, 1]).mass)

        return hist_dict


