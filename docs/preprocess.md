### Preprocess Events

* The next step is to preprocess events, which takes in the `JSON` configuration file from above and uses Coffeas' built in DataDiscoveryCLI class to create a list of all available file replicas. It then preprocesses them using Coffeas' preprocess function.
```
python3 scripts/preprocessed_json.py Run3Summer23BPix bkg
```
* The preprocessed file information is stored in an output `JSON` file in the directory `data/jsons`. This output `JSON` file can either then be given to the skimmer, or directly to the analyzer if skimming is not needed. For example, see [data/jsons/Run3Summer23BPix/Run3Summer23BPix_bkg_preprocessed.json](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/jsons/Run3Summer23BPix/Run3Summer23BPix_bkg_preprocessed.json)
