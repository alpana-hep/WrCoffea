from coffea import processor
import warnings
import modules
import awkward as ak
from coffea.analysis_tools import Weights

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

        channel = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']
        hists = {f"{process}_{flavor}_{mll}": modules.makeHistograms.eventHistos([flavor, mll]) for flavor in channel for mll in mass}

        for hist_name, hist_obj in hists.items():
            cut = resolved_selections & selections.all(*hist_obj.cuts)
            hist_obj.FillHists(events[cut], weights.weight()[cut])

        masses = {key: None for key in ["mlljj_tuple", "mljj_leadLep_tuple", "mljj_subleadLep_tuple"]}
        modules.mass.createMasses(masses, resolved_events)

        return {"mc": mc_campaign, "process": process, "dataset": dataset, "hist_dict":hists, "mass_dict":masses}

    def postprocess(self, accumulator):
        return accumulator
