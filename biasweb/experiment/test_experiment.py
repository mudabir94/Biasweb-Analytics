# import itertools
import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController
from biasweb.utils.Assigner import Assigner
from webapp.models import experiment as Experiment
from webapp.models import block as Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature


#%% RETRIEVE AN EXISTING EXPERIMENT
admin_id = "ses-007"
#e_id = admin_id + "-1234"
#^^^No longer needed as now controller will retrieve from database and compose
texp = ExperimentController(a_id=admin_id, e_id=9)
print("Exp Custom Id:",texp.exp.custom_exp_id)
#print("New Exp Custom Id:",nexp.exp.custom_exp_id)
print("The following features are set to be enabled:")
print(list(texp.fSet.all()))
#print(texp.fSet)

#%% CREATE A NEW EXPERIMENT
#nexp = ExperimentController(a_id=admin_id)
#print("NEW Exp Custom Id:",nexp.exp.custom_exp_id)
#%% TEST INDIV FEATURE MODIFICATION
fSymbol = 'W' #JUST TO test individual feature handling
xFSym = 'D' #Againd Ditto
levFSym= 'A' #FOR testing levels change in an existing feature
texp.addFeature(fSymbol)
texp.delFeature(fSymbol)
texp.addFeature(fSymbol=levFSymbol, byPrompt=True)
#texp.delFeature(levFSymbol)
#%% TEST FSET MODIFICATION (EN MASSE)
nFSym = 'C' #For testing the addition of new feature
newFSet = ['W','A',nFSym]  #please change depending on what's in the database
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

#%% Test BLOCK GENERATION -- only proceed if DB has feature levels
texp.generateBlocks()
print("List of blocks is as follows:")
for i,b in enumerate(texp.blocks):
    print(i,":", b)
#print(texp.blocks)
#TODO@SHAZIB: save to blocks in DB

#%%TEST ASSIGNMENT TO BATCHES AND BLOCKS
assigner = Assigner()

#%%TEST ASSIGNMENT ON RANDOMLY ASSEMBLED DB
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

#%%TEST ASSIGNER ON ACTUAL SAMPLE SUBJECTS DATA
fPath = "biasweb/utils/data/SampleExpData_oneSheet.xlsx"
assigner.getLocalDToAssign(fPath)

#%%TEST INTERACTIVE BATCH ASSIGNMENT WITHOUT BLOCKS EXISTING
print("EITHER identify a column no. for PRE-DEFINED Batching ")
print("OR ENTER 999 FOR SELF-DEFINED BATCHING")
print("OR just press ENTER to skip BATCHING:")
fields = assigner.df.columns
for i in range(len(fields)):
    print("[",i,"]",fields[i])
inputNo = eval(input("No of Batch Column?  "))
#%%IF SELF-DEFINED BATCHING
if inputNo == 999:
    no_batches = eval(input("Number of Batches? "))
    batchLabels = list()
    for j in range(no_batches):
        print("BATCH #",j+1,"\' OK? ")
        batchLabels.append(input() or (j+1))
    batchesTitle = input("Title as \'BATCHES\' or...?") or 'BATCHES'
    print("Using",batchesTitle,"as title for the",no_batches,"batches",batchLabels)
    dSubBatched = assigner.splitInBins(no_batches,batchesTitle, batchLabels)
    print(assigner.df.head())
elif inputNo:
    print(fields[batchColNo], ": Setting  as BATCH TITLE")
    texp.setBatchesTitle(fields[batchColNo])


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