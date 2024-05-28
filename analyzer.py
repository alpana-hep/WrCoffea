from coffea import processor
import warnings
import utils

warnings.filterwarnings("ignore",module="coffea.*")

class WrAnalysis(processor.ProcessorABC):
    def __init__(self):
        self.eejj_60mll150 = utils.makeHistograms.eventHistos(['eejj', '60mll150'])
        self.mumujj_60mll150 = utils.makeHistograms.eventHistos(['mumujj', '60mll150'])
        self.emujj_60mll150 = utils.makeHistograms.eventHistos(['emujj', '60mll150'])

        self.eejj_150mll400 = utils.makeHistograms.eventHistos(['eejj','150mll400'])
        self.mumujj_150mll400 = utils.makeHistograms.eventHistos(['mumujj','150mll400'])
        self.emujj_150mll400 = utils.makeHistograms.eventHistos(['emujj','150mll400'])

        self.eejj_400mll = utils.makeHistograms.eventHistos(['eejj','400mll'])
        self.mumujj_400mll = utils.makeHistograms.eventHistos(['mumujj','400mll'])
        self.emujj_400mll = utils.makeHistograms.eventHistos(['emujj','400mll'])

        self.hists = {
            "eejj_60mll150": self.eejj_60mll150,
            "mumujj_60mll150": self.mumujj_60mll150,
            "emujj_60mll150": self.emujj_60mll150,
            "eejj_150mll400": self.eejj_150mll400,
            "mumujj_150mll400": self.mumujj_150mll400,
            "emujj_150mll400": self.emujj_150mll400,
            "eejj_400mll": self.eejj_400mll,
            "mumujj_400mll": self.mumujj_400mll,
            "emujj_400mll": self.emujj_400mll
        }

    def process(self, events): #Processes a single NanoEvents chunk

        nevts = events.metadata["nevts"]
        print(f"Processing {nevts} events.")

        events = utils.objects.createObjects(events)
        selections = utils.selection.createSelection(events)

        resolved_selections = selections.all('exactly2l', 'atleast2j', 'leadleppt60', "mlljj>800", "dr>0.4")

        for hist_name, hist_obj in self.hists.items():
            hist_obj.FillHists(events[resolved_selections & selections.all(*hist_obj.cuts)])

        return {"nevents": {events.metadata["dataset"]: len(events)}, "hist_dict": self.hists}

    def postprocess(self, accumulator):
        return accumulator
