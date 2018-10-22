# import itertools
import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController
from biasweb.utils.Assigner import Assigner
from webapp.models import experiment as Experiment
from webapp.models import block as Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature

#print("As-Salaam Alaikum")
admin_id = "ses-007"
#exp_id = admin_id + "-1234"
#^^^No longer needed as now controller will retrieve from database and compose


texp = ExperimentController(a_id=admin_id, e_id=9)
#nexp = ExperimentController(a_id=admin_id)
print("Exp Custom Id:",texp.exp.custom_exp_id)
#print("New Exp Custom Id:",nexp.exp.custom_exp_id)
print("The following features are set to be enabled:")
print(list(texp.fSet.all()))
#print(texp.fSet)
#Set a different set of features

fSymbol = 'W' #JUST TO test individual feature handling
#xFSym = 'D' #Againd Ditto
nFSym = 'I' #For testing the addition of new feature
#levFSym= 'A' #TODO@SHAZIB: Test change levels of existing feature through add feature

texp.addFeature(fSymbol)
texp.delFeature(fSymbol)
newFSet = ['W','A','R']  #please change depending on what's in the database
#TODO@shazib: TEST setFSet
texp.setFSet(newFSet)
print(texp.fSet)
texp.saveExperiment()
#Edit feature levels
texp.autoSetFLevels(True)
print(texp.fLevels)
texp.saveExperiment()

#Test block generation
#list(itertools.product(*texp.fLevels.values()))
texp.generateBlocks()
print(texp.blocks)
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
# dPc = texp.assignToBlocks(df = dSub, batchField = 'group')
# dPc
assigner.getLocalDToAssign()
labels=['A','B','C']
no_batches=len(labels)
print(no_batches)
dSubBatches = assigner.splitInBins(no_batches,'batch', labels )
dSubBatches.get_group('A')

#Test block assignment
