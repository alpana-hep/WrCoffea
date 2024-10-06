#!/usr/bin/env python3
import math

def gamma(px_lead, py_lead, px_sublead, py_sublead):
    if px_lead > 0:
        gamma_lead = math.atan(py_lead/px_lead)
    if px_lead < 0:
        gamma_lead = math.atan(py_lead/px_lead) + math.pi

    if px_sublead > 0:
        gamma_sublead = math.atan(py_sublead/px_sublead)
    if px_sublead < 0:
        gamma_sublead = math.atan(py_sublead/px_sublead) + math.pi

    return gamma_lead, gamma_sublead

class Four_Vector:
    def __init__(self, e, px, py, pz, gamma_lead, gamma_sublead):
        self.e = e
        self.px = px
        self.py = py
        self.pz = pz
        self.px_leadprime = px*math.cos(gamma_lead) + py*math.sin(gamma_lead)
        self.py_leadprime = -px*math.sin(gamma_lead) + py*math.cos(gamma_lead)
        self.pz_leadprime = pz
        self.px_subleadprime = px*math.cos(gamma_sublead) + py*math.sin(gamma_sublead)
        self.py_subleadprime = -px*math.sin(gamma_sublead) + py*math.cos(gamma_sublead)
        self.pz_subleadprime = pz
