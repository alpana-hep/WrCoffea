### Create JSON configuration files

#### Make a template JSON file

* Create a template `.JSON` file in the foler `data/configs/Run3Summer23BPix`. This file contains the each [DAS](https://cmsweb.cern.ch/das/) dataset name, with metadata indicating the MC campaign, process, dataset, and cross-section. Input the cross-section from the previous section. Note that the sum of the weights should be `0.0` in this file. For example, see [data/configs/Run3Summer23BPix
/Run3Summer23BPix_bkg_template.json](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/configs/Run3Summer23BPix/Run3Summer23BPix_bkg_template.json)

#### Compute the Sum of the Event Weights

* To compute the sum of the weights, run the script
```
python3 scripts/make_config.py Run3Summer23BPix bkg
```
* This script takes in the `JSON` template file, computes the sum of the event weights (which needs to be tracked if the datasets are to be skimmed), and outputs the same `JSON` file with the sum of the weights included. For example, see [data/configs/Run3Summer23BPix
/Run3Summer23BPix_bkg_cfg.json](https://github.com/UMN-CMS/WrCoffea/blob/add_skims/data/configs/Run3Summer23BPix/Run3Summer23BPix_bkg_cfg.json)
