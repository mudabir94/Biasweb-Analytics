#0. IMPORT MODULES REQUIRED
import numpy as np
import pandas as pd
from biasweb.experiment.controller import ExperimentController, SubjCont
from biasweb.utils.assign import Assigner
from webapp.models import experiment as Experiment
from webapp.models import Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature
from webapp.models import User, Subject
from webapp.forms import SubjectCreationForm as scf

#0. Initialize phone
set1 = [91,14,49]
set2 = [43,6,101]
setDict = {1:set1, 2:set2} 

uid = 16010001
#1.1 Get list of experiments the user is a subject in
tuser = User.objects.get(username=uid)
subj_list = tuser.subject_set.all().prefetch_related('exp')
subj_list.values_list('id', 'exp')
#todo: complete the extraction of maximum experiment number

##[Alternative way to get to maximum experiment]
exp_list = tuser.subject_set.values_list('exp', flat=True) #PLEASE CHECK IF WE CAN GET PREFETCH RELATED HERE
exp_active = max(exp_list)
#1.2 Get experiment features list

#1.3 Get the subject id for that experiment
sId = subj_list.get(exp=exp_active).id

#2. Initialize test subject control
tscont = SubjCont(s_id=sId)
tscont.subject.exp  #Confirm the Experiment number of subject

#3. Get the block that subject is assigned to - this will tell us which features to enable
levsToSet = list(tscont.subject.block.levels_set)

#4. Get phone set if P is included in the block
for l in levsToSet:  #TODO - CLEAN OTHER FEATURES PREFIX TO MAKE THIS WORK (REMOVE \ AND "")
    print(l)
    pExists = l.find("P",0,1)
    print("FOUND?> ",pExists)
    if(l.find("P")!=-1):
        setNo = int(l.split(".")[1])
        print(setNo,"-phones: ",setDict[setNo])    
levsToSet


#3. RETRIEVE ACTIVE EXPERIMENT
# admin_id = "ses-007" #USING THE CUSTOM-ID OF SUPERUSER #2 (shazib [not dr.shazib]) ses-007 for Shazib
# init_expid = 7 #to be created after first new experient
# texp = ExperimentController(a_id=admin_id, e_id=init_expid) #9) #9 is prompt-based testing and #11 is web-based
# print("Exp Custom Id:",texp.exp.custom_exp_id)
# print("The following features are set to be enabled:")
# print(list(texp.fSet.all()))
