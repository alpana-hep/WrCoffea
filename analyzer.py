from coffea import processor
import warnings
import modules
import awkward as ak
from coffea.analysis_tools import Weights
import dask.array as da
import hist.dask as dah


warnings.filterwarnings("ignore",module="coffea.*")

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events): 

        mc_campaign = events.metadata["mc_campaign"]
        lumi = events.metadata["lumi"]
        process = events.metadata["process"]
        dataset = events.metadata["dataset"]
        x_sec = events.metadata["xsec"]

        print(f"Analyzing {len(events)} {dataset} events.")

        weights = Weights(size=None, storeIndividual=True)
        weights.add('eventWeight', events.genWeight/abs(events.genWeight))

        events = modules.objects.createObjects(events)
        selections = modules.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events=events[resolved_selections]

        npass = ak.num(resolved_events.leptons[:, 0].pt, axis=0).compute()
        print(f"{npass} events passed.")

        flavor = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']
#        hists = {f"{process}_{flavor}_{mll}": modules.makeHistograms.eventHistos([flavor, mll]) for flavor in channel for mll in mass}

#        for hist_name, hist_obj in hists.items():
#            cut = resolved_selections & selections.all(*hist_obj.cuts)
#            hist_obj.FillHists(events[cut], weights.weight()[cut])

        h = (
            dah.Hist.new.Reg(400, 0, 2000, name="pT_lead_lepton", label=r"p_{T} of the leading lepton [GeV]")
            .StrCat([], name="process", label="Process", growth=True)
            .StrCat([], name="channel", label="Channel", growth=True)
            .StrCat([], name="mll", label="Dilepton Mass", growth=True)
            .Weight()
        )

        for flav in flavor:
            for m in mass:
                cut = resolved_selections & selections.all(flav, m)
                h.fill(pT_lead_lepton=events[cut].leptons[:, 0].pt, process=process, channel=flav, mll=m)
        
        hist_dict = {"leadlepton_pt": h}

        masses = {key: None for key in ["mlljj_tuple", "mljj_leadLep_tuple", "mljj_subleadLep_tuple"]}
        modules.mass.createMasses(masses, resolved_events)

        return {"mc": mc_campaign, "process": process, "dataset": dataset, "hists": hist_dict, "mass_dict":masses}

    def postprocess(self, accumulator):
        return accumulator
