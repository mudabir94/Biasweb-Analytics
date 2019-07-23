#0. IMPORT MODULES REQUIRED
import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController
from biasweb.utils.assign import Assigner
from webapp.models import experiment as Experiment
from webapp.models import Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature
from webapp.models import User, Subject
from webapp.forms import SubjectCreationForm as scf
from webapp.models import selectedAdminPhones as PSets
from webapp.models import mobilephones as Phones

def setSelfDefinedBatches(expCont, defaultNo=None):
    if not defaultNo:
        no_batches = eval(input("Number of Batches? "))
        batchesLabels = list()
        for j in range(no_batches):
            batNo = j+1
            print("LABEL FOR BATCH ",batNo,"=",batNo,", CHANGE? ")
            batchesLabels.append(input() or (batNo))
        batchesTitle = input("Title as \'BATCHES\' or...?") or 'BATCHES'
        print("Using",batchesTitle,"as title for the",no_batches,"batches",batchesLabels)
        expCont.setBatchesTitle(batchesTitle)
        expCont.subjData = expCont.assigner.splitInBins(no_batches,batchesTitle, batchesLabels)
        return batchesTitle
    else:
        print("RECEIVED DEFAULT NO: ", defaultNo)
        batchesTitle = 'BATCHES'
        expCont.subjData = expCont.assigner.splitInBins(defaultNo, batchesTitle)
        expCont.setBatchesTitle(batchesTitle)
        return batchesTitle


def setPreDefinedBatches():
    pass

OUT_PATH="biasweb/data/output/"
interactive = False #Make True if you want this test to ask for field names mapping
feature_editing = True

#Initialize phone sets for adding as block feature levels
set1 = [91,14,49]
set2 = [43,6,101]
setDict = {1:set1, 2:set2}

## 1. RETRIEVE AN EXISTING EXPERIMENT

admin_id = "ses-007" #USING THE CUSTOM-ID OF SUPERUSER #2 (shazib [not dr.shazib]) ses-007 for Shazib
# init_expid = 42 #to be created after first new experient
# texp = ExperimentController(a_id=admin_id, e_id=init_expid) #9) #9 is prompt-based testing and #11 is web-based
# print("Exp Custom Id:",texp.exp.custom_exp_id)
# print("The following features are set to be enabled:")
# print(list(texp.fSet.all()))

## 2. CREATE A NEW EXPERIMENT
texp = ExperimentController(a_id=admin_id)
print("NEW Exp Custom Id:",texp.exp.custom_exp_id)
## 3. TEST INDIV FEATURE MODIFICATION
# if feature_editing:
fSymbol = 'W' #JUST TO test individual feature handling
xFSym = 'D' #Againd Ditto
levFSym= 'A' #FOR testing levels change in an existing feature
texp.addFeature(fSymbol)
texp.delFeature(fSymbol)
texp.addFeature(fSymbol=levFSym, byPrompt=True)
#texp.delFeature(levFSymbol)

## 4. TEST FSET MODIFICATION (EN MASSE) ----
nFSym = 'P' #For testing the addition of new feature
newFSet = ['W','A',nFSym]  #please change depending on what's in the database
texp.setFSet(newFSet,prompt=False)
set1 = [91,14,49]
set2 = [43,6,101]
setDict = {1:set1, 2:set2}
p_levList = list()
for key,s in setDict.items():
    print(key,":",s)
    p_set = Phones.objects.filter(id__in=s)
    p_levList.append('P.'+str(key))
    for count, i in enumerate(s):
        expPSets = PSets()
        expPSets.exp = texp.exp
        expPSets.pset_id= key
        expPSets.mob = p_set.get(id=i)
        expPSets.p_order = count
        expPSets.save()
print(PSets.objects.filter(exp_id = texp.exp.id))       

texp.addFeature('P', p_levList)




#newLevs = {'W': ['direct', 'AHP'], 'C': ['full', 'pruned']}
newLevs = {'W': ['direct', 'AHP'], 'A': ['all', '2by2','user'], 'R': ['0', '1']}
#TODO: Now need to differentiate between default/block features
#SE
texp.setFSet(newFLevels=newLevs,prompt=True)
texp.saveExperiment()
#Edit feature levels
#texp.autoSetFLevels(True)
print(texp.fLevels)
texp.saveExperiment()

## 5. Test BLOCK GENERATION -- only proceed if DB has feature levels
blocks = texp.generateBlocks()

##TEST ASSIGNMENT TO BATCHES AND BLOCKS
fPath = "biasweb/data/input/MBA_RCM1_SampleData.csv"
texp.importSujbectData(fPath)
#TODO@SHAZIB: for now assuming no appending to existing users
#print(texp.subjData)

##8.a OBTAIN DATA COL NAMES/FIELDS
fields = texp.getSubColNames()
if interactive:
    print("Which field will be used as CUSTOM ID")
    for i in range(len(fields)):
        print("[",i,"]",fields[i])
    customIdNo = eval(input("ENTER Column No for CUSTOM ID:  "))
    texp.setIdField(fields[customIdNo])
else:
    texp.setIdField(fields[0]) #Col 0 is assumed as ROLLNO
print("ID FIELD: ", texp.idField)
#texp.saveSubjects()

##TEST INTERACTIVE BATCH ASSIGNMENT (NO BLOCKS ASSIGNED YET)
if interactive:
    print("EITHER identify a column no. for PRE-DEFINED Batching ")
    print("OR ENTER 999 FOR texp-DEFINED BATCHING")
    print("OR just press ENTER to skip BATCHING:")
    for i in range(len(fields)):
        print("[",i,"]",fields[i])
    inputNo = eval(input("No of Batch Column?  "))
else:
    inputNo = 999 #Col 1 is assumed SECTION
print("INPUT NO:", inputNo)
##IF SELF-DEFINED BATCHING VS. PRE-DEFINED
if inputNo == 999:
    if interactive:
        batchesTitle = setSelfDefinedBatches(texp)
    else:
        batchesTitle = setSelfDefinedBatches(texp, defaultNo=3)
    print(texp.subjData.head())
elif inputNo:
    print(fields[inputNo], ": Setting  as BATCH TITLE")
    texp.setBatchesTitle(fields[inputNo])
    batchesLabels = texp.subjData.iloc[:,inputNo].unique()

batchesTitle = texp.exp.batches_title
texp.subjData.groupby(batchesTitle).size()
#TEST SINGLE SUBJECT BATCH UPDATE
# texp.exp.subject_set.filter(user__custom_id='16010075').update(batch='TEST')
# texp.exp.subject_set.get(user__custom_id='16010075').batch
# texp.updateOneBatch(subjC_Id='16010075')

#TEST BULK UPDATE OF CHANGE TO BATCHES AND THEN CHECK
batchesTitle = setSelfDefinedBatches(texp, defaultNo=3)
texp.subjData.groupby(batchesTitle).size()
texp.updateAllBatches() #MAKE SURE TO CALL IF YOU CHANGED THE BATCHES


texp.saveSubjects()
texp.deleteAllSubjects()

breakUp = texp.assignToBlocks() #retruns a dataframe of groupby sizes (unstacked for batchwise breakup)
breakUp.to_json(orient='index') #FOR ROW-WISE printing in HTML as json object

tpvt = pd.pivot_table(
        data=texp.subjData,
        index='block__serial_no',
        columns=texp.exp.batches_title,
        values=texp.idField,
        aggfunc='count',
        margins=True,
        margins_name='Total'
)
tpvt.columns = tpvt.columns.droplevel(0)
tpvt = tpvt.rename(
    columns={
        tpvt.columns[-1]:'Block Total'
    }
)
print(tpvt)
tpvt.to_json(orient='columns')



texp.saveSubjects(writeXL=True) #DEFAULT FILE NAME IS CUSTOM_EXP_ID
#texp.getBlockedGroups()
#texp.getBlockedDict()

# #texp.updateBatch DOES NOT EXIST 
# #TODO@SHAZIB

# #Assuming we will label blocks
# GpLabel = 'block' #FOR TESTING ONLY
# # TESTING SIMPLE BIN SPLIT ON SUBJECTS
# # NOTE: WILL NOT ASSIGN IN PROPORTION TO BATCHES
# texp.assigner.splitInBins(4,binName=GpLabel,binLabels=[1,2,3,4])
# #CHECK PERCENTAGES AFTER SIMPLE ASSIGNMENT
# (texp.subjData.groupby([GpLabel,batchesTitle])
#     .size()
#     .groupby(level=0)
#     .apply(lambda x: x/float(x.sum())))

# #CORRECT ASSIGNEMENT in PC of Batches
# dSub = texp.subjData
# #Calculating pc-wise break-up of batches for later comparison
# #DOES NOT affect any assignments done later.
# dfGpCount = dSub.groupby(texp.exp.batches_title).size().to_frame(name = 'split_edges')
# total = dSub.shape[0]
# dfGpPc = dfGpCount.apply(lambda x: x / total)
# dPc = dfGpPc.reset_index()

# #When we apply splitInBins batch-wise, the break-up will automatically be 
# #closer to actual batch proportions
# dSubByGp = texp.assigner.splitByField(
#                     nBins=4,
#                     bName=GpLabel,
#                     fieldName=batchesTitle,
#                     data=dSub
# )
            
# (dSubByGp.groupby([GpLabel,batchesTitle])
#     .size()
#     .groupby(level=0)
#     .apply(lambda x: x/float(x.sum())))

# print("SHOULD BE:")
# dPc

# #ONLY USE FOLLOWING WHERE WE JUST WANT _ADDITIONAL_ COLUMN
# #DO NOT USE _assignByPc_ for pre-defined batches
# dAss = (dSub.groupby(GpLabel, group_keys=False)
#             .apply(texp.assigner.assignByPc, dPc))
# dSub[GpLabel] = dAss
# (dSub.groupby([batchesTitle,GpLabel])
#     .size()
#     .groupby(level=0)
#     .apply(lambda x: x/float(x.sum())))

#Test block assignment
#TODO@SHAZIB: NOW CREATE BLOCKS FIRST AND ASSIGN TO EACH BLOCK IN PROPORTION TO SECTIONS
#WORKFLOW:
#1. DONE: Setup write of subjects (with self/pre-defined batches to database)
#2. DONE: Setup write of blocks to database
#3. Assign subjects to blocks
# texp.assigner.df
#3.a. If batches pre-exist: ask whether AssignmentByPc?
#3.b. If batches do not exist, do direct Assignment ... later batch assignment will
#     automatically be propotionate, TODO: TEST BOTH CASES IN ANY CASE
#4. WRITE EXCEL FILE

writer = pd.ExcelWriter(OUT_PATH+texp.exp.custom_exp_id+'.xlsx')
texp.subjData.to_excel(writer, sheet_name='PD_ASSIGNED')
writer.save()