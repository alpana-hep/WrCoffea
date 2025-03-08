
```
https://twiki.cern.ch/twiki/bin/viewauth/CMS/LumiRecommendationsRun2
```


```
ssh wijackso@lxplus.cern.ch
```

```
source /cvmfs/cms-bril.cern.ch/cms-lumi-pog/brilws-docker/brilws-env
```

```
brilcalc lumi -u /fb --byls -b "STABLE BEAMS" --normtag /cvmfs/cms-bril.cern.ch/cms-lumi-pog/Normtags/normtag_PHYSICS.json --output-style csv -i /afs/cern.ch/cms/CAF/CMSCOMM/COMM_DQM/certification/Collisions18/13TeV/Legacy_2018/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt > lumi2018.csv
```
