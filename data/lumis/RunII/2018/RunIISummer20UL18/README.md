### Luminosity
```
https://twiki.cern.ch/twiki/bin/viewauth/CMS/LumiRecommendationsRun2
```
The golden JSON for `RunIISummer20UL18` is
```
https://cms-service-dqmdc.web.cern.ch/CAF/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt
```

The LUM POG recommendation is to always calculate the integrated luminosity with the JSON actually used for every analysis. This should be done with the brilcalc tool.

This is done from lxplus. For istance,
```
ssh wijackso@lxplus.cern.ch
source /cvmfs/cms-bril.cern.ch/cms-lumi-pog/brilws-docker/brilws-env
```

Use the command below,
```
brilcalc lumi -u /fb --byls -b "STABLE BEAMS" --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --output-style csv -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt > lumi2018.csv
```
