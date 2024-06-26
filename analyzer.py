from coffea import processor
import warnings
import modules
from coffea.analysis_tools import Weights
warnings.filterwarnings("ignore",module="coffea.*")
import numpy as np
import awkward as ak
import hist.dask as dah
import hist
import dask_awkward as dak

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events): 

        mc_campaign = events.metadata["mc_campaign"]
        lumi = events.metadata["lumi"]
        process = events.metadata["process"]
        dataset = events.metadata["dataset"]
        x_sec = events.metadata["xsec"]

        eventWeight = np.sign(events.genWeight)

        sumw = ak.sum(eventWeight, axis=0)

        print(f"Analyzing {len(events)} {dataset} events.")
        
        if process != "Signal":
            weights = Weights(size=None, storeIndividual=True)
            weights.add("event_weight", weight=eventWeight)
            
        events = modules.objects.createObjects(events)
        selections = modules.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events=events[resolved_selections]

        flavor = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']
    
        hists = modules.histograms.create_histograms()
        hist_dict = modules.histograms.fill_histograms(hists, events, selections, resolved_selections, process, flavor, mass, weights)
        
        masses = {key: None for key in ["mlljj", "mljj_leadLep", "mljj_subleadLep"]}
        modules.mass.createMasses(masses, resolved_events)

        return {"mc": mc_campaign, "process": process, "dataset": dataset, "x_sec": x_sec, "sumw": sumw, "hists":  hist_dict, "mass_tuples":masses}

    def postprocess(self, accumulator):
        return accumulator
