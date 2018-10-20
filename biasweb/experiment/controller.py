# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 15:57:03 2018

@author: Dr. Shazib Sh
"""

#from biasweb.experiment import Experiment
import itertools
import pandas as pd
from biasweb.utils.Assigner import Assigner
from webapp.models import experiment as Experiment
from webapp.models import block as Block
from webapp.models import experiment_feature as Feature

#    STATUS LEVELS:
DESIGN_MODE = 'DESIGN_MODE' #Under Construction
READY = 'READY' #Design complete + Subjects List attached
OPEN = 'OPEN' #READY + login shared w/ Subjects
ACTIVE = 'ACTIVE' #Subject(s) are undergoing experiment
INACTIVE = 'INACTIVE' #Partially completed but no Subjects
CLOSED = 'CLOSED' #No longer accepting Subjects - awaiting analysis
SUSPENDED = 'SUSPENDED' #Not accepting Subjects - could be reopened - some design changes allowed
CANCELLED = 'CANCELLED' #Abandoned - not accepting subjects ever
ANALYZED = 'ANALYZED' #Analysis Reports 

class ExperimentController:
    def __init__(self, a_id, fSet = None, cap = 100):
        self.exp = Experiment()
        self.exp.status = DESIGN_MODE
        self.exp.custom_exp_id = a_id
        exp_id = 1 + Experiment.objects.latest('id').id
        exp_id = '-' + str(exp_id).zfill(4)  #ensuring the id is now a 4 digit numeric string
        self.exp.custom_exp_id += exp_id
        self.exp.capacity = cap            #Capacity to budget for experiment
        self.admin_id = a_id      #TODO@MUDABIR - NEED TO MODIFY EXPERIMENT ADMIN IMPLEMENTATION
        self.fLevels = {}
        if fSet:
            self.fSet = fSet
        else:
            self.fSet = [   'I',    #I = Interactivity
                            'R',    #R = Revisability
                            'W',    #W = Weight generation method - direct or ahp
                            'A',    #A = Alternative display method (e.g., phones to choose from)
                                    #    all, 1by1, 2by2, user
                            'C'     #C = Criteria display mehtod (e.g. memory, os, etc.)
                                    #    prune,full, self-extended [0,1,2]
            ]

    def saveExperiment(self):
        #Check necessary fields and set STATUS
        #Write to DB
        self.exp.save()
        #Write Experiment Features by first checking against exsiting Platform Features
        #save block

    def setFeatures(self, fSet):
        self.fSet = fSet

    def clarifyFeature(self, enquiry):
        levToPop = '999'
        for f in enquiry:
            
          
            flevList=self.fLevels[f]
            
            while len(levToPop) > 0:
                
                print("Feature",f,"has the following factor levels.")
                
                for i,l in enumerate(flevList):
                    print("[",i,"] = ",l)
                levToPop = input("Enter numbers for level to drop: ")
                if(len(levToPop)>0):
                    #fLevList = self.fLevels[f]
                    print(len(levToPop))
                    flevList.pop(eval(levToPop))
                    print(flevList)

            return flevList

                            
    def setFeatureLevels(self, fLevels):
        print("asdasd",fLevels)
        self.fLevels = fLevels
        print('in feature levels')

    def autoSetFLevels(self, byPrompt = False):
        if byPrompt: enquiry = []
        for f in self.fSet:
            if f=='I' or f=='R' or f=='C':
                self.fLevels[f] = [0,1]
            if f=='W':
                self.fLevels[f] = ["direct", "ahp"]
            if f=='A':
                self.fLevels[f] = ["all", "1by1", "2by2", "user"]
                if byPrompt:
                    enquiry.append(f)
                    self.fLevels[f] = self.clarifyFeature(enquiry)
        print(self.fLevels[f])

    def generateBlocks(self):
        self.blocks = list(
            itertools.product(
                *self.fLevels.values()
            )
        )
        """ print("List of blocks is as follows:")
        for i,b in enumerate(self.blocks):
            print(i,":", b) """

    def writeBlocks(self):
        print("1st Block Set: ")
        print(self.blocks)
        #MUST TEST FOR EXPERIMENT WRITE BEFORE
        #WRITING TO BLOCK
        # cBlockSet = Block(
        #     used_in = 
        # )
        #1. get Experiment object from models
        #2. write to correct blocks field
        #3. 



    #TODO: Work on Blocks to Students Assignment
    #1. (?) use workaround OR implement blocks writing to Blocks model
    #2. USE OTHER METHOD --> retrieve block list/block id for experiment
    #3. check if batches have been assigned and which is the field
    #4. DONE --> implement batches as part of experiment model
    #5. Check proportions to be kept for batches (if existing)
    #5.5 Ask if proportions are wanted based on any other field
    #6. Assign to blocks in given proportions of batches
    # def assignToBlocks(self, df, blockSet = None, batchField = None):
    #     print('I was called with field:', batchField)
    #     assigner = Assigner()
    #     #GET batches for this experiment
    #     if batchField:
    #         #Calculate the proportions of each batch
    #         #For now working with default
    #         dfBatchCount = df.groupby(batchField).size().to_frame(name = 'split_edges')
    #         dfBatchPc = dfBatchCount.apply(lambda x: x / x.sum())
    #         dfBatchPc = dfBatchPc.reset_index()
    #         #assigner.assignByPc(df, dfBatchPc)
    #         #Need to use apply method on each Block so first a group by should run
   #         #Pass to assign funciton of Assigner APPLY SEPARATELY FOR EACH GROUP