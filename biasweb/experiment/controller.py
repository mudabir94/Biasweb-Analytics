# -*- coding: utf-8 -*-
"""
Created on Mon Oct  8 15:57:03 2018

@author: Dr. Shazib Sh
"""

#from biasweb.experiment import Experiment
import itertools

class ExperimentController:
    def __init__(self, id, a_id, fSet = [], cap = 50):
        self.exp_id = id            #Will actually be set by retrieving index from database
        self.cap = cap              #Capacity to budget for experiment
        self.admin_id = a_id
        self.fLevels = {}
        if len(fSet) > 0:
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

                            
    
    def setFeatureLevels(self):
        enquiry = []
        for f in self.fSet:
            if f=='I' or f=='R' or f=='C':
                self.fLevels[f] = [0,1]
            if f=='W':
                self.fLevels[f] = ["direct", "ahp"]
            if f=='A':
                self.fLevels[f] = ["all", "1by1", "2by2", "user"]
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

  