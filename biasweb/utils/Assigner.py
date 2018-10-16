"""
Utility to randomly allocate experiment subjects (as DataFrame)
to batches/blocks or any other group
"""
# Importing the libraries
import numpy as np
#import matplotlib.pyplot as plt
import pandas as pd
from tkinter import *
from tkinter.filedialog import askopenfilename

#%%
class Assigner:
    def __init__(self, df):
        self.df = df

    #%%The function that assigns a DataFrame (gp) RANDOMLY into k groups
    # returns Series containing randomly permutated labels of k groups
    def assign(self, k):
        buckets = pd.qcut(
                      np.arange(self.df.shape[0]), #a vector of the indices of the dataframe  
                      q=k,
                      labels=range(k) #NEEDS TO BE CUSTOMISED SO USER CAN GIVE LABELS
                                        #DEFAULT SHOULD START WITH 1 NOT 0
                    ).get_values()
        buckets = buckets[np.random.permutation(self.df.shape[0])]
        return pd.Series( buckets, index=self.df.index)
            
    #%%return assignment as a groupedby object
    # 
    def splitInBins(self, k, binName):
        self.df[binName] = self.assign(k)
        groups = self.df.groupby(binName)
        print(groups.size())
        return groups
    
    def splitByField(self, fieldName):
        groups = self.df.groupby(fieldName)
        print(groups.size())
        return groups
            
    #%%
    def assignAutoTest(self):
        self.df = pd.DataFrame({'customer_id': np.random.normal(size=10000),
                   'group': np.random.choice(['a','b','c'], size=10000)})
        proportions = {'a':[.5,.5],'b':[.4,.6], 'c':[.2,.8]}
        self.df.head()
        self.df['batch'] = self.assign(self,3) #allocate df rows into three batches

        (self.df.groupby(['group','batch'])
            .size()
            .unstack())  #create a sort of pivot table


    #%% NOW TESTING ON A FILE
    def getLocalDToAssign(self):
        #from tkinter.filedialog import asksaveasfilename

        # Read in a file and evaluate its format [Excel or CSV]
        fToUpload = askopenfilename()
        print(fToUpload)
        qMoreInput = False
        qMoreInput, dToAssign, xlSheets = \
            self.extractData(fToUpload)
        if qMoreInput:
            #qMoreInput True means it is an XL file AND has more sheets
            print("The XL file has the following sheets:")
            for i in range(0,len(xlSheets)):
                print("[",i+1,"] = ",xlSheets[i])
            xlShNo = eval(input("Enter the sheet number required: "))
            print("Running extractData again, with xlShNo =",xlShNo)
            qMoreInput, dToAssign, xlSheets = \
                    self.extractData(fToUpload, xlShNo)
        self.df = dToAssign
        #return dToAssign
        
    #%%
    # Extracts a pandas DataFrame from a given CVS or XLS file
    # returns: needShNo = whether we need selection of sheet number
    def extractData(self, fName, shNo = 0):
        f = fName #This funciton assumes self was initialized with df as path to the df file
        needShNo = False
        sheets = []
        dta = pd.DataFrame()
        #If CSV, assume first line is the headline
        if f.endswith('.csv'):
                dta = pd.read_csv(f)
                print(dta.head())
                self.df = dta
                return needShNo, self.df, sheets
            #If EXCEL, detect first line
        if f.endswith('.xlsx') or f.endswith('.xls'):
            xlFile = pd.ExcelFile(f)
            sheets = xlFile.sheet_names
            if shNo == 0:
                print(sheets)
                if len(sheets) > 1:
                    needShNo = True
                    return needShNo, dta, sheets
                else:
                    shNo = 1
            dta = xlFile.parse(sheets[shNo-1])
            needShNo = False
            print(dta.head())
            self.df = dta
            return needShNo, self.df, sheets
                        
#%%
# if xl file then we need to know which sheet to open
# so we will return the Sheet Names and Set our attrib type to CSV/XL
# else just return the data

# a separate function will take the function name
# it will determine which line the data is on
# and then read in the data to dToAssign

    

    
#%%ORIGINAL CODE FOR ALLOCATING BY CERTAIN PROPORTIONS OF A GIVEN GROUP
#def assigner(gp):
#    group = gp['group'].iloc[0]
#     ...:     cut = pd.qcut(
#                  np.arange(gp.shape[0]), 
#                  q=np.cumsum([0] + proportions[group]), 
#                  labels=range(len(proportions[group]))
#              ).get_values()
#     ...:     return pd.Series(cut[np.random.permutation(gp.shape[0])],
#                               index=gp.index,
#                               name='assignment')
#     ...:
#
# to obtain pivot table
# pd.pivot_table(df,index=['Group'],values=["customer_id"],aggfunc=lambda x: len(x.unique()))
