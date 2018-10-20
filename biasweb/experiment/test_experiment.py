# import itertools
import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController
from biasweb.utils.Assigner import Assigner

#print("As-Salaam Alaikum")
admin_id = "ses-007"
#exp_id = admin_id + "-1234"
#^^^No longer needed as now controller will retrieve from database and compose


t_exp = ExperimentController(admin_id)
print("Exp Custom Id:",t_exp.exp.custom_exp_id)
print("--> The following features will be enabled:")
print(t_exp.fSet)
#Set a different set of features
newFSet = ['W','A','C']
t_exp.setFeatures(newFSet)
print(t_exp.fSet)
t_exp.saveExperiment()
#Edit feature levels
t_exp.autoSetFLevels(True)
print(t_exp.fLevels)

#Test block generation
#list(itertools.product(*t_exp.fLevels.values()))
t_exp.generateBlocks()
print(t_exp.blocks)
#Test batch assignment
assigner = Assigner()
#TODO: On view, implement a subject files import method
#assigner.getLocalDToAssign() #Open file
assigner.assignAutoTest()

#dSubBatches = assigner.splitInBins(3,'batch' )
#dSubBatches.get_group(0).head() #Batch 0 members summary/head
dSub = assigner.df
dSub.groupby('group').size()


#Test block assignment
# dPc = t_exp.assignToBlocks(df = dSub, batchField = 'group')
# dPc
assigner.getLocalDToAssign()
labels=['A','B','C']
no_batches=len(labels)
print(no_batches)
dSubBatches = assigner.splitInBins(no_batches,'batch', labels )
dSubBatches.get_group('A')

#Test block assignment
