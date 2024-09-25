import awkward as ak
from coffea.nanoevents import NanoEventsFactory, NanoAODSchema
import hist
import uproot

NanoAODSchema.warn_missing_crossrefs = False

fname = "95537AFE-1978-A847-A49E-5ABDE5F9D8B5.root"
events = NanoEventsFactory.from_root(
    {fname: "Events"},
    schemaclass=NanoAODSchema,
    metadata={"dataset": "UL18NanoAODv9/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8"},
).events()

# Explore the file
print(f"\nThe fields in the Events tree are:\n{events.fields}")
print(f"\nThe branches in GenJet are:\n{events.GenJet.fields}")
print(f"\nThe GenJet pTs are: {events.GenJet.pt.compute()}")
print(f"The number of GenJets are: {ak.num(events.GenJet, axis=1).compute()}")
print(f"The total number of events is {ak.num(events.GenJet, axis=0).compute()}\n")

# Make object level cut by only keeping jets with pT > 20
selectedJets = events.GenJet[(events.GenJet.pt > 20)]
events["selectedJets"] = selectedJets
print("Now requiring that the GenJet pT > 20 GeV:")
print(f"The GenJet pTs are: {events.selectedJets.pt.compute()}")
print(f"The number of GenJets are: {ak.num(events.selectedJets, axis=1).compute()}")
print(f"The total number of events is {ak.num(events.selectedJets, axis=0).compute()}\n")

# Make event level cut by only keeping events with exactly 4 jets
fourJets = (ak.num(events.selectedJets, axis=1) == 4)
fourJetEvents = events[fourJets]
print("Looking at the events with 4 GenJets")
print(f"The GenJet pTs are: {fourJetEvents.selectedJets.pt.compute()}")
print(f"The number of GenJets are: {ak.num(fourJetEvents.selectedJets, axis=1).compute()}")
print(f"The total number of events is {ak.num(fourJetEvents.selectedJets, axis=0).compute()}\n")

# Fill a histogram of the Lead Jet pT for events with exactly 4 GenJets, each GenJet with a pT > 20.
print(f"The leading GenJet pT is {fourJetEvents.selectedJets[:, 0].pt.compute()}")
histogram = hist.Hist.new.Reg(100, 0, 1000, label="pT of the leading GenJet [GeV]").Weight()
histogram.fill(fourJetEvents.selectedJets[:, 0].pt.compute(), weight=1)

# Save histogram as a ROOT file
print(f"Saved histogram to output_histogram.root")
with uproot.recreate("output_histogram.root") as f:
    f["leading_jet_pt"] = histogram
