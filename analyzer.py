from coffea import processor
import warnings
import modules
from coffea.analysis_tools import Weights
warnings.filterwarnings("ignore",module="coffea.*")
import numpy as np
import awkward as ak
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

#        eventWeight = events.genWeight/abs(events.genWeight)
#        sumw = ak.sum(eventWeight, axis=0)
#        x_sec = ak.Array(len(events)*[x_sec])
#        my_weights = eventWeight*x_sec/sumw

#        weights = Weights(size=None, storeIndividual=True)
#        weights.add('myweights', my_weights)

        events = modules.objects.createObjects(events)
        selections = modules.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events=events[resolved_selections]

        flavor = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']

        hists = modules.histograms.create_histograms()
        hist_dict = modules.histograms.fill_histograms(hists, events, selections, resolved_selections, process, flavor, mass)

        masses = {key: None for key in ["mlljj", "mljj_leadLep", "mljj_subleadLep"]}
        modules.mass.createMasses(masses, resolved_events)

        return {"mc": mc_campaign, "process": process, "dataset": dataset, "hists": hist_dict, "mass_tuples":masses}

    def postprocess(self, accumulator):
        return accumulator
