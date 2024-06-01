from coffea import processor
import warnings
import modules

warnings.filterwarnings("ignore",module="coffea.*")

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        channel = ['eejj', 'mumujj', 'emujj']
        mass = ['60mll150', '150mll400', '400mll']

        self.hists = {}
        for flavor in channel:
            for mll in mass:
                hist_key = f"{flavor}_{mll}"
                self.hists[hist_key] = modules.makeHistograms.eventHistos([flavor, mll])

        self.mass = {}
        self.mass["mlljj_tuple"] = None
        self.mass["mljj_leadLep_tuple"] = None
        self.mass["mljj_subleadLep_tuple"] = None

    def process(self, events): 

        dataset = events.metadata["dataset"]
        mc = events.metadata["mc_campaign"]
        print(f"Analyzing {len(events)} {mc}_{dataset} events.")

        events = modules.objects.createObjects(events)
        selections = modules.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")
        resolved_events = events[resolved_selections]

        for hist_name, hist_obj in self.hists.items():
            if "vals" not in hist_name:
                hist_obj.FillHists(events[resolved_selections & selections.all(*hist_obj.cuts)])

        modules.mass.createMasses(self.mass, resolved_events)

        return {"mc":mc, "process":events.metadata["process"], "hist_dict":self.hists, "mass_dict":self.mass}

    def postprocess(self, accumulator):
        return accumulator
