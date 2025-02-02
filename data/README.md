## Data
This directory stores input data for the analysis.
*	**Directories**:
    *   `configs/`: Contains the beginning configuration files. There is a configuration file for each MC campaign. This file consists of each datasets DAS name, with metadata specifying the physics process, MC campaign, and the sum of the event weights (which is needed for analyzing skimmed files). For each era, there is a seperate configuration file for MC and data.
    *   `jsons/`: Contains files that are similar to the configuration files, except that they also contain all of the filenames and replica sites. The files have also been preprocessed with Coffea's `preprocess` function. These files are given to the analyzer or the skimmer.
    *   `miniaod/`: Miniaod files are needed to compute each datasets cross-section. In this directory there are txt files for each MC campaign, consisting of a list of all of the miniAOD DAS dataset names. There are also directories for each MC campaign, with a `txt` file for each dataset consisting of the filepaths for every `ROOT` file.
    *   `x-secs/`: Contains directories for each MC campaign. In each directory is a `log` file for each dataset, consisting of the computed cross-section from `GenXsecAnalyzer`.
