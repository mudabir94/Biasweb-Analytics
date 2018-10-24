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
from webapp.models import Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature
from webapp.models import User, Subject


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
    def __init__(self, a_id, e_id = None, cap = 100):
        self.exp = Experiment()
        self.fLevels = {}
        self.subjData = pd.DataFrame()
        self.subjects = Subject()
        if e_id:
            self.exp = Experiment.objects.get(id=e_id)
            self.fSet = self.exp.experiment_feature_set.select_related('p_feature')
            self.fLevels = self.retrieveFLevels()
        else:
            self.exp.status = DESIGN_MODE
            self.exp.owner = User.objects.get(custom_id=a_id)      #TODO@MUDABIR - NEED TO MODIFY EXPERIMENT ADMIN IMPLEMENTATION
            
            self.exp.custom_exp_id = 'TBA' #can only be created after Experient table assigns an id
            self.exp.capacity = cap            #Capacity to budget for experiment
            self.saveExperiment()
            self.exp.custom_exp_id = a_id
            exp_id = self.exp.id
            exp_id = '-' + str(exp_id).zfill(4)  #ensuring the id is now a 4 digit numeric string
            self.exp.custom_exp_id += exp_id
            self.saveExperiment()

    def saveExperiment(self):
        #Check necessary fields and set STATUS
        #Create and Write Experiment in DB
        self.exp.save()
        #Create and Write Feature with fSet in DB
        #Create and Write Batches with batch_title
        #Create and Write Blocks in DB
        #WRITE SUBJECTS to Subject Database

    #def saveFSet(self):    
        #assumes setFeatures has been called to add new features

    def setBatchesTitle(self, btLabel):
        self.exp.batches_title = btLabel
        self.exp.save()
        print("Batches Title set to: ",self.exp.batches_title)

    def getFSet(self):
        return list(self.fSet.all())
    """
    setFSet
    Inputs: Either newFSet (list of feature_symbols for features to be set)
            OR newFLevels (dictionary with symbols as key pointing to chosen list of levels)
    """
    def setFSet(self, newFSet=None, newFLevels=None, prompt = False):
        #check whether FSet or FLevels
        if newFLevels:
            print("New Levels have been supplied - extracting FSet...")
            newFSet = list(newFLevels.keys())
        #3 things
        #1. add all features (incl existing) in newFSet along with any new LevList
        for f in newFSet:
            nLev = None
            if newFLevels:
                nLev = newFLevels[f]
            self.addFeature(fSymbol=f, newLevList=nLev, byPrompt=prompt)
        #2. compare the existing fSet with proposed, and identify diffs
        curFSet = list(self.fSet.values_list('p_feature__feature_symbol', flat=True))
        dropFList = list(set(curFSet)-set(newFSet))
        #3. delete any features not required
        for d in dropFList:
            self.delFeature(d)
        #self.fSet.bulk_create(self.fInSet)

    
    def addFeature(self, fSymbol, newLevList = None, byPrompt = False):
        pf = PFeature.objects.filter(feature_symbol=fSymbol)[0]
        if newLevList:
            print("New Levels for ",fSymbol," are: ",newLevList)
            self.fLevels[fSymbol] = newLevList
        elif fSymbol not in self.fLevels:
            self.fLevels[fSymbol] = pf.feature_levels
        #check if feature already exists, else create
        expF = self.fSet.filter(p_feature__feature_symbol=fSymbol)
        if expF.exists():
            print(expF[0].p_feature.feature_name,": This feature already exists.")
            if newLevList:
                expF.update(chosen_levels = newLevList)
                print(expF[0].chosen_levels)
            return expF[0]
        else:
            if not newLevList and byPrompt and len(self.fLevels[fSymbol])>2:
                enq = [fSymbol]
                fList = self.clarifyFeature(enq)
                print(fList)
                self.fLevels[fSymbol] = fList
            newEF = self.exp.experiment_feature_set.create(
                    p_feature = pf,
                    chosen_levels = self.fLevels[fSymbol]          
            )
            return newEF
    
    def delFeature(self,fSymbol):
        expF = self.getFeature(fSymbol)
        if expF:
            expF.delete()
            del self.fLevels[fSymbol]

    def getFeature(self,fSymbol):
        expF = self.fSet.filter(p_feature__feature_symbol=fSymbol)
        if expF.exists():
            return expF[0]
        else:
            return None

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

    def retrieveFLevels(self):
    #only for setting fLevels afresh by unpacking QuerySet
        for f in self.fSet.all():
            self.fLevels[f.p_feature.feature_symbol] = f.chosen_levels
        return self.fLevels

    # def setFeatureLevels(self, fLevels):
    #     self.fLevels = fLevels

    # def autoSetFLevels(self, byPrompt = False):
    #     if byPrompt: enquiry = []
    #     for f in self.fSet:
    #         if f=='I' or f=='R' or f=='C':
    #             self.fLevels[f] = [0,1]
    #         if f=='W':
    #             self.fLevels[f] = ["direct", "ahp"]
    #         if f=='A':
    #             self.fLevels[f] = ["all", "1by1", "2by2", "user"]
    #             if byPrompt:
    #                 enquiry.append(f)
    #                 self.fLevels[f] = self.clarifyFeature(enquiry)
    #     print(self.fLevels[f])

    def generateBlocks(self):
        self.blocks = list(
            itertools.product(
                *self.fLevels.values()
            )
        )
        self.saveBlocks()
    
    def saveBlocks(self):
        print("List of blocks is as follows:")
        blocksInDb = list()
        for i,b in enumerate(self.blocks):
            newBlock = Block()
            newBlock.used_in = self.exp
            newBlock.serial_no = i+1
            newBlock.levels_set = list(b)
            blocksInDb.append(newBlock)
        print(blocksInDb)
        self.exp.block_set.bulk_create(blocksInDb)

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

    def importSujbectData(self,iFile):
        self.assigner = Assigner()
        self.assigner.getLocalDToAssign(iFile)
        self.subjData = self.assigner.df


    #TODO: Work on Blocks to Students Assignment
    #1. (?) use workaround OR implement blocks writing to Blocks model
    #2. USE OTHER METHOD --> retrieve block list/block id for experiment
    #3. check if batches have been assigned and which is the field
    #5. Check proportions to be kept for batches (if existing)
    #5.5 Ask if proportions are wanted based on any other field
    #6. Assign to blocks in given proportions of batches
    def assignToBlocks(self, blockSet = None):
        #GET batches for this experiment
        if self.exp.batches_title:
            #Calculate the proportions of each batch
            #For now working with default
            dfBatchCount = self.subjData.groupby(self.exp.batches_title).size().to_frame(name = 'split_edges')
            dfBatchPc = dfBatchCount.apply(lambda x: x / x.sum())
            dfBatchPc = dfBatchPc.reset_index()
            #assigner.assignByPc(df, dfBatchPc)
            #Need to use apply method on each Block so first a group by should run
            #Pass to assign funciton of Assigner APPLY SEPARATELY FOR EACH GROUP
    
    def saveSubjects(self, dSub, fName=None):
        if not self.subjData:
            self.subjData = dSub
        #WRITE TO DATABASE
        #if not self.subjects.pk:

        #WRITE TO FILE AS WELL, IF GIVEN
        #ELSE DEFAULT TO CUSTOM-ID WITH CERTAIN SWITCHES