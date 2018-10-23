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
#levFSym= 'A' #TODO@SHAZIB: Test change levels of existing feature through add feature

#texp.addFeature(fSymbol)
#texp.delFeature(fSymbol)
nFSym = 'C' #For testing the addition of new feature
newFSet = ['W','A',nFSym]  #please change depending on what's in the database
#TODO@shazib: TEST setFSet
texp.setFSet(newFSet,prompt=True)
print(texp.fSet.all())
#newLevs = {'W': ['direct', 'AHP'], 'C': ['full', 'pruned']}
newLevs = {'W': ['direct', 'AHP'], 'A': ['all', '2by2','user'], 'R': ['0', '1']}

texp.setFSet(newFLevels=newLevs,prompt=True)
texp.saveExperiment()
#Edit feature levels
#texp.autoSetFLevels(True)
print(texp.fLevels)
texp.saveExperiment()

#Test block generation
#list(itertools.product(*texp.fLevels.values()))
texp.generateBlocks()
print("List of blocks is as follows:")
for i,b in enumerate(texp.blocks):
    print(i,":", b)
#print(texp.blocks)
#Test batch assignment
assigner = Assigner()
#TODO: On view, implement a subject files import method
#assigner.getLocalDToAssign() #Open file
assigner.assignAutoTest()

#dSubBatches = assigner.splitInBins(3,'batch' )
#dSubBatches.get_group(0).head() #Batch 0 members summary/head
dSub = assigner.df
dSub.groupby('group').size()
#Following operations are simply to make uneven groups to test
#reassignment correction.
dSub.groupby(['batch','group']).size().unstack()
dSub = dSub[dSub.batch != 'C'] #Just keeping two batches
dSub.groupby(['group','batch']).size().unstack()
dSub = dSub[~((dSub.group == 'c') & (dSub.batch == 'A'))] #Making group c unevenly distributed
dSub.groupby(['group','batch']).size().unstack()
#Test block assignment
GpLabel = 'group'
BatchLabel = 'batch'
dfGpCount = dSub.groupby(GpLabel).size().to_frame(name = 'split_edges')
total = dSub.shape[0]
dfGpPc = dfGpCount.apply(lambda x: x / total)
#TODO@SHAZIB: Add Column and then convert to dictionary
dPc = dfGpPc.reset_index()
dPc
dAss = (dSub.groupby(BatchLabel, group_keys=False)
            .apply(assigner.assignByPc, dPc))
dSub[GpLabel] = dAss
dSub.groupby(['assigned','batch']).size().unstack()
#TODO@SHAZIB: ASSIGNMENT BY PROPORTIONS NEEDS TO BE FIXED TO TWO LEVEL THROUGH APPLY
assigner.getLocalDToAssign()
labels=[1,2]
no_batches=len(labels)
print(no_batches)
dSubBatched = assigner.splitInBins(no_batches,BatchLabel, labels )
GpLabel = 'SECTION'
#CHECK PERCENTAGES AFTER BATCH ASSIGNMENT
(assigner.df.groupby([BatchLabel,GpLabel])
    .size()
    .groupby(level=0)
    .apply(lambda x: x/float(x.sum())))
print("SHOULD BE:")
#CORRECT BATCH ASSIGNEMENT PC  -- NOT NEEDED IN GENERAL - BUT PRE-TESTING FOR BLOCK ASSIGNMENT
dSub = assigner.df
dfGpCount = dSub.groupby(GpLabel).size().to_frame(name = 'split_edges')
total = dSub.shape[0]
dfGpPc = dfGpCount.apply(lambda x: x / total)
#TODO@SHAZIB: Add Column and then convert to dictionary
dPc = dfGpPc.reset_index()
dPc
dAss = (dSub.groupby(BatchLabel, group_keys=False)
            .apply(assigner.assignByPc, dPc))
dSub[GpLabel] = dAss
(dSub.groupby([BatchLabel,GpLabel])
    .size()
    .groupby(level=0)
    .apply(lambda x: x/float(x.sum())))

#Test block assignment
#TODO@SHAZIB: NOW CREATE BLOCKS FIRST AND ASSIGN TO EACH BLOCK IN PROPORTION TO SECTIONS