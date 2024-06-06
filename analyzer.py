from coffea import processor
import warnings
import modules
import awkward as ak

warnings.filterwarnings("ignore",module="coffea.*")

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        pass

    def process(self, events): 

        mc = events.metadata["mc_campaign"]
        process = events.metadata["process"]
        dataset = events.metadata["dataset"]
        print(f"Analyzing {len(events)} {dataset} events.")

        events = modules.objects.createObjects(events)
        selections = modules.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events=events[resolved_selections]

        channel = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']
        hists = {f"{process}_{flavor}_{mll}": modules.makeHistograms.eventHistos([flavor, mll]) for flavor in channel for mll in mass}

#        num_selected = ak.num(resolved_events.leptons,axis=0).compute()
#        print(f"{num_selected} events passed the selection ({num_selected/len(events)*100:.2f}% efficiency).\n")

        for hist_name, hist_obj in hists.items():
            if "vals" not in hist_name:
                hist_obj.FillHists(events[resolved_selections & selections.all(*hist_obj.cuts)])

        masses = {key: None for key in ["mlljj_tuple", "mljj_leadLep_tuple", "mljj_subleadLep_tuple"]}
        modules.mass.createMasses(masses, resolved_events)

        return {"mc": mc, "process": process, "dataset": dataset, "hist_dict":hists, "mass_dict":masses}

    def postprocess(self, accumulator):
        return accumulator
