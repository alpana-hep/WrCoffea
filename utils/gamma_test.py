#!/usr/bin/env python3

from prime_frame import *

px_lead = [60, -100, 73, 59]
py_lead = [34, 29, 97, 40]
px_sublead = [-12, 25, 10, -17]
py_sublead = [15, 14, 9, 16]

gamma_lead_list = []
gamma_sublead_list = []

for indx in range(0, len(px_lead)): #this breaks the columnar approach of Coffea
    gamma_lead, gamma_sublead = gamma(px_lead[indx], py_lead[indx], px_sublead[indx], py_sublead[indx])

    gamma_lead_list.append(gamma_lead)
    gamma_sublead_list.append(gamma_sublead)

print("gamma_lead_list --> " + str(gamma_lead_list))
print("gamma_sublead_list --> " + str(gamma_sublead_list))
