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

#1. Retrieve user subjects and experiments
uid = 16010001
<<<<<<< HEAD
exp=Experiment.objects.get(pk=41)

print(exp)
expid=443
tscont = SubjCont(u_id=uid)
=======
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
>>>>>>> 462e2215182105b427156229f901f41beab8c677
tscont.subject.exp