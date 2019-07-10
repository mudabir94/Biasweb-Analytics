###
# TO TEST NULL FEATURE SET HANDNLING
###

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

OUT_PATH="biasweb/data/output/"
#interactive = False #Make True if you want this test to ask for field names mapping
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

## 2. CREATE A NEW EXPERIMENT
texp = ExperimentController(a_id=admin_id)
print("NEW Exp Custom Id:",texp.exp.custom_exp_id)
## 3. TEST INDIV FEATURE MODIFICATION
# if feature_editing:
fSymbol = 'W' #JUST TO test individual feature handling
xFSym = 'I' #Againd Ditto
levFSym= 'A' #FOR testing levels change in an existing feature
texp.addFeature(fSymbol)
texp.addFeature(xFSym)
print("The following features are set to be enabled:")
print(list(texp.fSet.all()))
print(texp.retrieveFLevels())

texp.delFeature(fSymbol)
texp.delFeature(xFSym)
print(texp.retrieveFLevels())

# texp.addFeature(fSymbol=levFSym, byPrompt=True)
# texp.delFeature(levFSym)
# print(list(texp.fSet.all()))
# print(texp.retrieveFLevels())

## 4. TEST FSET MODIFICATION (EN MASSE) ----
#Edit feature levels
nFSym = 'P' #For testing the addition of new feature
newFSet = ['W','A',nFSym]  #please change depending on what's in the database
texp.setFSet(newFSet,prompt=False)
print(texp.retrieveFLevels())
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
print(texp.retrieveFLevels())

#5. Replace Fset with a NULL SET using setFSet only
#@MUDABIR - NOTE THAT WE JUST MAKE newFSet=[] (not None)
#to ensure the delete operation works
texp.setFSet(newFSet=[],prompt=False)
print(texp.retrieveFLevels())
texp.setFSet(newFSet=newFSet)
print(texp.retrieveFLevels())
#SO IT WORKS EVEN AFTER EMPTYING THE SET

#texp.autoSetFLevels(True)
print(texp.fLevels)
#texp.saveExperiment()
