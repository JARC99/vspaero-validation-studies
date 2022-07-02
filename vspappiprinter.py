# -*- coding: utf-8 -*-
"""
Created on Sat Jul  2 10:41:34 2022

@author: jaros
"""

import openvsp as vsp

print(vsp.ListAnalysis())

analysis_name = 'VSPAEROSweep'


print("\n\n")
print(vsp.GetAnalysisInputNames( analysis_name ))
