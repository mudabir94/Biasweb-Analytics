# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 15:57:03 2018

@author: Dr. Shazib Shaikh
"""

#from biasweb.experiment import Experiment
import itertools
import pandas as pd
from biasweb.utils.assign import Assigner
from webapp.models import experiment as Experiment
from webapp.models import Block
from webapp.models import experiment_feature as ExpFeature
from webapp.models import platform_feature as PFeature
from webapp.models import User, Subject
from webapp.forms import SubjectCreationForm as scf

# WHERE SAVED FILES WILL BE STORED
OUT_PATH="biasweb/data/output/"

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
        self.idField = None
        self.assigner = Assigner()
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
            self.fSet = self.exp.experiment_feature_set
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
            fName = expF.p_feature.feature_name
            expF.delete()
            del self.fLevels[fSymbol]
            print("DELETED",fName)

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
        return self.exp.block_set
    
    def saveBlocks(self):
        if self.exp.block_set.exists():
            print("Deleting pre-existing blocks")
            self.exp.block_set.all().delete()
        print("List of blocks to GENERATE is as follows:")
        blocksInDb = list()
        for i,b in enumerate(self.blocks):
            newBlock = Block()
            newBlock.used_in = self.exp
            newBlock.serial_no = i+1
            newBlock.levels_set = list(b)
            blocksInDb.append(newBlock)
        print(*blocksInDb, sep="\n")
        #print(list(blocksInDb))
        self.exp.block_set.bulk_create(blocksInDb)
        

    def importSujbectData(self,iFile):
        self.assigner.getLocalDToAssign(iFile)
        self.subjData = self.assigner.df
        if self.idField:
            setIdField(self.idField)

    def setIdField(self, idFName):
        self.idField = idFName
        print('outside if condition of not empty')
        if not self.subjData.empty:
            print('if subjdata not empty')
            self.subjData[idFName] = self.subjData[idFName].astype(str)
            print('self.subjData[idFName]:')
            print(self.subjData[idFName])
    def getSubColNames(self):
        cols = self.subjData.columns
        return cols
    
    def updateOneBatch(self, subjId=None, subjC_Id=None):
        batchField = self.exp.batches_title
        
        if batchField:
            #retrieve based on subjId,
            if subjId:
                subj = self.exp.subject_set.get(id=str(subjId))
            #or based on subjC_id
            elif subjC_Id:
                subj = self.exp.subject_set.get(user__custom_id=str(subjC_Id))
            if subj:
                print("Going to update:",subj,"having batch",subj.batch)
                subjNewBatch = self.subjData[
                    self.subjData[self.idField] == subj.user.custom_id
                ]
                print("Will use this record to update: ")
                print(subjNewBatch)
                subj.batch = subjNewBatch[batchField].iloc[0]
                subj.save()
            #else print error and pass
            else:
                print("NOT FOUND: subject to update appears to not exist.")
        else:
            print("NO BATCH FIELD assigned for experiment")
    
    def updateAllBatches(self, newBatchTitle=None):
        """
        Update the existing batch allocations, 
        or nominate a new (self-defined) batch column.
        Assumes the batches are to be updated based on
        current state in self.subjData
        """
        #Check if we need to reset the batchTitle
        if newBatchTitle:
            self.setBatchesTitle(newBatchTitle)
        for i, sub in self.subjData.iterrows():
            self.updateOneBatch(subjC_Id=sub[self.idField])

    def assignToBlocks(self, blockSet = None):
        """
        Adds/updates block column of subjData and its database table.
        Parameters
        ----------
        blockSet: List of tuples in the order of the features defined.
            This is an optional argument.  By default the blocks in self.blocks will
            be used, assuming that generateBlocks and saveBlocks have been called.
        Returns
        -------
        blocksBreakUp: a DataFrame with size statistics. If subjects have been assigned,
            it provides a batch-wise breakup count.
        """
        #GET blocks number and labels
        blockCount = self.exp.block_set.count()
        blockBinName = 'block__serial_no'
        batchField = self.exp.batches_title
        print('batch Field',batchField)
        print('batch Field type',type(batchField))
        #GET batches for this experiment
        if batchField: 
            print('in BatchField')  
            print('blockCount',blockCount)  
            print('blockBinName',blockBinName) 
            print('batchField',batchField) 
            self.dSubByBlock = self.assigner.splitByField(
                        nBins=blockCount,
                        bName=blockBinName,
                        fieldName=batchField,
                        
            )
            print('self.dSubByBlock')
            print(self.dSubByBlock)
            #PERCENTAGE BREAKUP AFTER ASSIGNMENT
            print(self.dSubByBlock.groupby([blockBinName,
                                    batchField])
                    .size()
                    .groupby(level=0)
                    .apply(lambda x: x/float(x.sum())))
            #'SHOULD BE' PERCENTAGE
            print("SHOULD BE:")
            dfBatchCount = self.subjData.groupby(batchField).size().to_frame(name = 'split_edges')
            dfBatchPc = dfBatchCount.apply(lambda x: x / x.sum())
            dfBatchPc = dfBatchPc.reset_index()
            print(dfBatchPc)
        else:
            print('in splitin bins field')
            self.dSubByBlock = self.assigner.splitInBins(
                no_bins=blockCount,
                binName=blockBinName
            )
        
        #ADD BLOCK_IDs from database (mapped to their serial_no)
        blockDict = dict(self.exp.block_set.values_list('serial_no','id'))
        self.dSubByBlock['block_id'] = self.dSubByBlock.block__serial_no.map(blockDict)
        subjSet = self.exp.subject_set
        for index, subj in self.dSubByBlock.iterrows():
            c_id=subj[self.idField]
            b_id=subj['block_id']
            subjSet.filter(user__custom_id=c_id).update(block_id=b_id)
        subjSetList = list(self.exp.subject_set.values()) #just to refresh subject_set in cache
        # if self.exp.batches_title:
        #     print(pd.DataFrame(subjSetList)
        #             .groupby(['block_id','batch'])
        #             .size().unstack())
        self.subjData = self.dSubByBlock
        blocksBreakUp = pd.pivot_table(
                self.subjData,
                index=blockBinName,
                columns=batchField,
                aggfunc='count',
                values=['ROLLNO'],
                margins=True,
                margins_name='Total'
            )
        blocksBreakUp.columns = blocksBreakUp.columns.droplevel(0)
        blocksBreakUp = blocksBreakUp.rename(
            columns={
                blocksBreakUp.columns[-1]:'Block Total'
            }
        )
        blocksBreakUp = blocksBreakUp.rename_axis("Block No.")
        return blocksBreakUp

    def saveSubjToXL(self, fName):
        writer = pd.ExcelWriter(OUT_PATH + fName + '.xlsx')
        self.subjData.to_excel(writer, sheet_name='Subjects')
        writer.save()
            
    def deleteAllSubjects(self):
        print('subject set',self.exp.subject_set.all())
        self.exp.subject_set.all().delete()
        self.exp.batches_title = None
        print('subject set',self.exp.subject_set.all())
        print('self.exp.batches_title',self.exp.batches_title)

        self.saveExperiment()
        
        
    def saveSubjects(self, dSub=None, writeXL=False, fName=None):
        if isinstance(dSub,pd.DataFrame):
            self.subjData = dSub
        #WRITE TO DATABASE
        #obtain set of existing users
        currUsers = User.objects.values_list('custom_id', flat=True)
        print(currUsers)
        #check if subjects exist for this exp object
        if not self.subjects.pk:
            subjForDb = list()
            #for every entry in the DataFrame
            for index, subj in self.subjData.iterrows():
                c_id = str(subj[self.idField])
                if c_id in currUsers:
                    print("User already exists - re-using existing user")
                    subj_id = User.objects.get(custom_id=c_id).id
                else:
                    print(index,": New User! Custom id will be -->",c_id)
                    subjUser = scf().save(commit=False, pwd=c_id)
                    subjUser.username = c_id
                    subjUser.custom_id = c_id
                    subjUser.save()
                    subj_id = subjUser.id
                #TODO@SHAZIB: CHECK IF SUBJECT USER EXISTS IN EXPERIMENT
                oldSubj = self.exp.subject_set.filter(user_id = subj_id)
                if oldSubj.exists():
                    print("Subject is already enrolled on the experiment")
                    print(oldSubj[0])
                    subject = oldSubj[0]
                    #IF EXISTS STILL UPDATE WITH BATCH/BLOCK - TODO SEE DJANGO BULK UPDATE PACKAGE
                else:
                    subject = Subject()
                    subject.user_id = subj_id
                    subject.exp = self.exp
                    if self.exp.batches_title:
                        subject.batch = subj[self.exp.batches_title]
                    subject.status = DESIGN_MODE
                    subjForDb.append(subject)
            print(subjForDb)
            self.exp.subject_set.bulk_create(subjForDb)
        if writeXL:
            if not fName:
                fName = self.exp.custom_exp_id
            self.saveSubjToXL(fName)


    
    def toString():
        print("This class is the Controler Class");