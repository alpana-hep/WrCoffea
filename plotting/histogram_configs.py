import numpy as np

configurations = {
"pt_leadlep": {
    "xlabel": "Lead lepton $p_{T}$ (GeV)",
    "60mll150": {
        "bins": list(range(0, 1020, 20)),
        "ylabel": "Events / 20 GeV",
        "xlim": (0, 1e3),
        "ylim": (1,6e4),
    },
    "150mll400": {
        "bins": list(range(0, 2010, 10)),
        "ylabel": "Events / 10 GeV",
        "xlim": (0, 2e3),
        "ylim": (0,1e4),
    },
    "400mll": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 1e3),
        "ylim": (1e-3, 2e3),
    }
},
"pt_subleadlep": {
    "xlabel": "Sublead lepton $p_{T}$ (GeV)",
    "60mll150": {
        "bins": list(range(0, 520, 20)),
        "ylabel": "Events / 20 GeV",
        "xlim": (0, 1e3),
        "ylim": (1, 1e4)
    },
    "150mll400": {
        "bins": list(range(0, 2010, 10)),
        "ylabel": "Events / 10 GeV",
        "xlim": (1, 2e3),
        "ylim": (1, 6e4)
    },
    "400mll": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 1e3),
        "ylim": (1e-3, 7e3),
    }
},
"pt_leadjet": {
    "xlabel": "$p_{T}$ of the leading jet (GeV)",
    "60mll150": {
        "bins": [0, 40, 100, 200, 400, 600, 800, 1000, 1500, 2000],
        "ylabel": "Events / 40 GeV",
        "xlim": (0, 2e3),
        "ylim": (1, 2e5)
    },
    "150mll400": {
        "bins": list(range(0, 2010, 50)),
        "ylabel": "Events / 10 GeV",
        "xlim": (0, 2e3),
        "ylim": (1, 2e4)
    },
    "400mll": {
        "bins": list(range(0, 2100, 100)),
        "ylabel": "Events / 100 GeV",
        "xlim": (0, 2e3),
        "ylim": (1, 2e4)
    }
},
"pt_subleadjet": {
    "xlabel": "$p_{T}$ of the subleading jet (GeV)",
    "60mll150": {
        "bins": list(range(0, 520, 20)),
        "ylabel": "Events / 20 GeV",
        "xlim": (0, 500),
        "ylim": (1, 2e4)
    },
    "150mll400": {
        "bins": list(range(0, 1010, 10)),
        "ylabel": "Events / 10 GeV",
        "xlim": (1, 1e3),
        "ylim": (1, 2e4)
    },
    "400mll": {
        "bins": list(range(0, 2010, 10)),
        "ylabel": "Events / 10 GeV",
        "xlim": (0, 2e3),
        "ylim": (1, 2e4)
    }
},
"pt_dileptons": {
    "xlabel": "$p_{T}^{ll}$ (GeV)",
    "60mll150": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 1e3),
        "ylim": (1, 5e6)
    },
    "150mll400": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 1e3),
        "ylim": (1, 6e4)
    },
    "400mll": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 2e3),
        "ylim": (1, 6e4)
    }
},
"pt_dijets": {
    "xlabel": "$p_{T}^{jj}$ (GeV)",
    "60mll150": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 1e3),
        "ylim": (1, 5e6)
    },
    "150mll400": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 1e3),
        "ylim": (1, 6e4)
    },
    "400mll": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / 50 GeV",
        "xlim": (0, 2e3),
        "ylim": (1, 6e4)
    }
},
"eta_leadlep": {
    "xlabel": "$\eta$ of the leading lepton",
    "60mll150": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    }
},
"eta_subleadlep": {
    "xlabel": "$\eta$ of the leading lepton",
    "60mll150": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    }
},
"eta_leadjet": {
    "xlabel": "$\eta$ of the leading jet",
    "60mll150": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    }
},
"eta_subleadjet": {
    "xlabel": "$\eta$ of the subleading jet",
    "60mll150": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-3, 3.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-3, 3),
        "ylim": (1e-3, 2e3)
    }
},
"phi_leadlep": {
    "xlabel": "$\phi$ of the leading lepton",
    "60mll150": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    }
},
"phi_subleadlep": {
    "xlabel": "$\phi$ of the leading lepton",
    "60mll150": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / 0.5",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    }
},
"phi_leadjet": {
    "xlabel": "$\phi$ of the leading jet",
    "60mll150": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    }
},
"phi_subleadjet": {
    "xlabel": "$\phi$ of the subleading jet",
    "60mll150": {
        "bins": list(np.arange(-4, 4, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "150mll400": {
        "bins": list(np.arange(-4, 4, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    },
    "400mll": {
        "bins": list(np.arange(-4, 4.5, 0.5)),
        "ylabel": "Events / bin",
        "xlim": (-4, 4),
        "ylim": (1e-3, 2e3)
    }
},
"mass_dileptons": {
    "xlabel": "$m_{ll}$ (GeV)",
    "60mll150": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / bin",
        "xlim": (0, 1000),
        "ylim": (1, 2e3)
    },
    "150mll400": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / bin",
        "xlim": (0, 1000),
        "ylim": (1, 2e3)
    },
    "400mll": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / bin",
        "xlim": (0, 1000),
        "ylim": (1, 2e3)
    },
},
"mass_dijets": {
    "xlabel": "$m_{jj}$ (GeV)",
    "60mll150": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / bin",
        "xlim": (0, 1000),
        "ylim": (1, 2e3)
    },
    "150mll400": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / bin",
        "xlim": (0, 1000),
        "ylim": (1, 2e3)
    },
    "400mll": {
        "bins": list(range(0, 1050, 50)),
        "ylabel": "Events / bin",
        "xlim": (0, 1000),
        "ylim": (1, 2e3)
    },
},
"mass_threeobject_leadlep": {
    "xlabel": "$m_{ljj}^{lead lep}$ (GeV)",
    "60mll150": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 2e3)
    },
    "150mll400": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 2e3)
    },
    "400mll": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 2e3)
    },
},
"mass_threeobject_subleadlep": {
    "xlabel": "$m_{ljj}^{sublead lep}$ (GeV)",
    "60mll150": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 2e3)
    },
    "150mll400": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 2e3)
    },
    "400mll": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 2e3)
    },
},
"mass_fourobject": {
    "xlabel": "$m_{lljj}$ (GeV)",
    "60mll150": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 9e3)
    },
    "150mll400": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 9e3)
    },
    "400mll": {
        "bins": [800,1000,1200,1400,1600,2000,2400,2800,3200,8000],
        "ylabel": "Events / bin",
        "xlim": (0, 8000),
        "ylim": (1, 9e3)
    },
},
}


