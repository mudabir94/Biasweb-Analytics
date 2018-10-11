
from biasweb.experiment.experiment import ExperimentController
from biasweb.utils.Assigner import Assigner
import itertools
import numpy as np
import pandas as pd

#print("As-Salaam Alaikum")
admin_id = "ses-007"
exp_id = admin_id + "-123"

t_exp = ExperimentController(exp_id, admin_id)
print(t_exp.exp_id,"--> The following features will be enabled:")
print(t_exp.fSet)
#Set a different set of features
newFSet = ['W','A','C']
t_exp.setFeatures(newFSet)
print(t_exp.fSet)

#Edit feature levels
t_exp.setFeatureLevels()
print(t_exp.fLevels)

#Test block generation
#list(itertools.product(*t_exp.fLevels.values()))
t_exp.generateBlocks()

#Test batch assignment
assigner = Assigner(pd.DataFrame())

#Test block assignment