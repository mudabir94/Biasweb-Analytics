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

#1. Initialize test subject control
uid = 16010001
exp=Experiment.objects.get(pk=41)

print(exp)
expid=443
tscont = SubjCont(u_id=uid,e_id=expid)
tscont.subject.exp