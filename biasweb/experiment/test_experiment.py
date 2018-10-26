#%%0. IMPORT MODULES REQUIRED
import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController
from biasweb.utils.Assigner import Assigner
from webapp.models import experiment as Experiment
from webapp.models import Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature
from webapp.models import User, Subject
from webapp.forms import SubjectCreationForm as scf

OUT_PATH="biasweb/data/output/"
#%% 1. RETRIEVE AN EXISTING EXPERIMENT
admin_id = "ses-001" #USING THE CUSTOM-ID OF SUPERUSER #1
#^^^SUBSTITUE WITH YOUR OWN - ELSE DEFAULT IS THE ONE WITH ID=1
texp = ExperimentController(a_id=admin_id, e_id=9)
print("Exp Custom Id:",texp.exp.custom_exp_id)
#print("New Exp Custom Id:",nexp.exp.custom_exp_id)
print("The following features are set to be enabled:")
print(list(texp.fSet.all()))
#print(texp.fSet)

#%% 2. CREATE A NEW EXPERIMENT
#nexp = ExperimentController(a_id=admin_id)
#print("NEW Exp Custom Id:",nexp.exp.custom_exp_id)
#%% 3. TEST INDIV FEATURE MODIFICATION
fSymbol = 'W' #JUST TO test individual feature handling
xFSym = 'D' #Againd Ditto
levFSym= 'A' #FOR testing levels change in an existing feature
texp.addFeature(fSymbol)
texp.delFeature(fSymbol)
texp.addFeature(fSymbol=levFSym, byPrompt=True)
#texp.delFeature(levFSymbol)

#%% 4. TEST FSET MODIFICATION (EN MASSE) ----
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

#%% 5. Test BLOCK GENERATION -- only proceed if DB has feature levels
texp.generateBlocks()
#print(texp.blocks)
#TODO@SHAZIB: save to blocks in DB

#%%TEST ASSIGNMENT TO BATCHES AND BLOCKS
#NEW: NOW ASSIGNER IS INSIDE CONTROLLER
#CREATED ON IMPORT OF SUBJECTS!!
#assigner = Assigner()


#%%7. TEST ASSIGNER ON ACTUAL SAMPLE SUBJECTS DATA
fPath = "biasweb/utils/data/SampleExpData_oneSheet.xlsx"
#assigner.getLocalDToAssign(fPath)
#NEW: use controller to access files now
texp.importSujbectData(fPath)
#TODO@SHAZIB: for now assuming no appending to existing users
#NEED TO REFINE STORAGE IF A LIST OF SUBJECTS ALREADY IS STORED
print(texp.subjData)

#%%8.a OBTAIN DATA COL NAMES/FIELDS
fields = texp.getSubColNames()
print("Which field will be used as CUSTOM ID")
for i in range(len(fields)):
    print("[",i,"]",fields[i])
customIdNo = eval(input("ENTER Column No for CUSTOM ID:  "))
texp.setIdField(fields[customIdNo])

#%%8.b FOR TESTING THIS SAMPLE DATA ONLY!!
texp.setIdField(fields[0])
texp.saveSubjects()

#%%TEST INTERACTIVE BATCH ASSIGNMENT WITHOUT BLOCKS EXISTING
print("EITHER identify a column no. for PRE-DEFINED Batching ")
print("OR ENTER 999 FOR texp-DEFINED BATCHING")
print("OR just press ENTER to skip BATCHING:")
for i in range(len(fields)):
    print("[",i,"]",fields[i])
inputNo = eval(input("No of Batch Column?  "))
#%%IF SELF-DEFINED BATCHING OR PRE-DEFINED
if inputNo == 999:
    no_batches = eval(input("Number of Batches? "))
    batchesLabels = list()
    for j in range(no_batches):
        print("BATCH #",j+1,"\' OK? ")
        batchesLabels.append(input() or (j+1))
    batchesTitle = input("Title as \'BATCHES\' or...?") or 'BATCHES'
    print("Using",batchesTitle,"as title for the",no_batches,"batches",batchesLabels)
    dSubBatched = texp.assigner.splitInBins(no_batches,batchesTitle, batchesLabels)
    print(texp.assigner.df.head())
elif inputNo:
    print(fields[inputNo], ": Setting  as BATCH TITLE")
    texp.setBatchesTitle(fields[inputNo])
    batchesLabels = texp.subjData.iloc[:,inputNo].unique()

#%% JUST TESTING - WHILE ASSUMING SECTIONS ARE BLOCKS
#NOTE: NOT MEANT FOR FRONT-END IMPLEMENTATION
GpLabel = 'SECTION'
#CHECK PERCENTAGES AFTER BATCH ASSIGNMENT
(texp.subjData.groupby([batchesTitle,GpLabel])
    .size()
    .groupby(level=0)
    .apply(lambda x: x/float(x.sum())))
print("SHOULD BE:")
#CORRECT BATCH ASSIGNEMENT PC  -- NOT NEEDED IN GENERAL - BUT PRE-TESTING FOR BLOCK ASSIGNMENT
dSub = texp.subjData
dfGpCount = dSub.groupby(GpLabel).size().to_frame(name = 'split_edges')
total = dSub.shape[0]
dfGpPc = dfGpCount.apply(lambda x: x / total)
#TODO@SHAZIB: Add Column and then convert to dictionary
dPc = dfGpPc.reset_index()
dPc
dAss = (dSub.groupby(batchesTitle, group_keys=False)
            .apply(texp.assigner.assignByPc, dPc))
dSub[GpLabel] = dAss
(dSub.groupby([batchesTitle,GpLabel])
    .size()
    .groupby(level=0)
    .apply(lambda x: x/float(x.sum())))

#Test block assignment
#TODO@SHAZIB: NOW CREATE BLOCKS FIRST AND ASSIGN TO EACH BLOCK IN PROPORTION TO SECTIONS
#WORKFLOW:
#1. Setup write of subjects (with self/pre-defined batches to database)
#2. Setup write of blocks to database
#3. Assign subjects to blocks
#3.a. If batches pre-exist: ask whether AssignmentByPc?
#3.b. If batches do not exist, do direct Assignment ... later batch assignment will
#     automatically be propotionate, TODO: TEST BOTH CASES IN ANY CASE
#4. WRITE EXCEL FILE
writer = pd.ExcelWriter(OUT_PATH+'Sample_SelfDefBatches_NoBlocks.xlsx')
dSub.to_excel(writer, sheet_name='SF_BATCH_ASSIGN')
writer.save()