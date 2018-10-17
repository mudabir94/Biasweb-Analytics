# import itertools
# import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController
from biasweb.utils.Assigner import Assigner

#print("As-Salaam Alaikum")
admin_id = "ses-007"
exp_id = admin_id + "-1234"

t_exp = ExperimentController(exp_id, admin_id)
print(t_exp.exp_id,"--> The following features will be enabled:")
print(t_exp.fSet)
#Set a different set of features
newFSet = ['I','W','A','C']
t_exp.setFeatures(newFSet)
print(t_exp.fSet)

#Edit feature levels
t_exp.setFeatureLevels()
print(t_exp.fLevels)

#Test block generation
#list(itertools.product(*t_exp.fLevels.values()))
t_exp.generateBlocks()
print(t_exp.blocks)
#Test batch assignment
assigner = Assigner(pd.DataFrame())
#TODO: On view, implement a subject files import method
#assigner.getLocalDToAssign()


assigner.getLocalDToAssign()
dSubBatches = assigner.splitInBins(3,'batch' )
dSubBatches.get_group(0)
#Test block assignment