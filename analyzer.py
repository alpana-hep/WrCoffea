from coffea import processor
import warnings
import utils

warnings.filterwarnings("ignore",module="coffea.*")

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        channel = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']

        self.hists = {}
        for flavor in channel:
            for mll in mass:
                hist_key = f"{flavor}_{mll}"
                self.hists[hist_key] = utils.makeHistograms.eventHistos([flavor, mll])

        self.hists["mlljj_vals"] = None
        self.hists["mljj_leadLep_vals"] = None
        self.hists["mljj_subleadLep_vals"] = None

    def process(self, events): 

        nevts = events.metadata["nevts"]
        print(f"Processing {nevts} events.")

        events = utils.objects.createObjects(events)
        selections = utils.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events = events[resolved_selections]

        utils.mass.createMasses(self.hists, resolved_events)

        for hist_name, hist_obj in self.hists.items():
            if "vals" not in hist_name:
                hist_obj.FillHists(events[resolved_selections & selections.all(*hist_obj.cuts)])

        return {"nevents": {events.metadata["dataset"]: len(events)}, "hist_dict": self.hists}

    def postprocess(self, accumulator):
        return accumulator
