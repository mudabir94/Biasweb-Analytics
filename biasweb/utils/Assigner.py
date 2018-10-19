"""
Utility to randomly allocate experiment subjects (as DataFrame)
to batches/blocks or any other group
"""
# Importing the libraries
import numpy as np
import pandas as pd
from tkinter import *
from tkinter.filedialog import askopenfilename

#%%
class Assigner:
    def __init__(self, df = None):
        self.df = df

    #%%The function that assigns a DataFrame (gp) RANDOMLY into k groups
    # returns Series containing randomly permutated labels of k groups
    def assign(self, no_batches,labels):
        buckets = pd.qcut(
                      np.arange(self.df.shape[0]), #a vector of the indices of the dataframe  
                      q=no_batches,
                      labels=labels #NEEDS TO BE CUSTOMISED SO USER CAN GIVE LABELS
                                          #DEFAULT SHOULD START WITH 1 NOT 0
                      #labels=['A','B','C']
                    ).get_values()
        buckets = buckets[np.random.permutation(self.df.shape[0])]
        return pd.Series( buckets, index=self.df.index)
            
    #%%return assignment as a groupedby object
    # 
    def splitInBins(self, no_batches, binName,labels):
        self.df[binName] = self.assign(no_batches,labels)
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
        self.proportions = {'a':[.5,.5],'b':[.4,.6], 'c':[.2,.8]}
        print(self.df.head())
        self.df['batch'] = self.assign(3) #allocate df rows into three batches

        print(self.df.groupby(['group','batch'])
            .size()
            .unstack()
            .assign())  #create a sort of pivot table

    #def calcSplitRatio():
        #Input: Series or List of batches
        #Output: dictionary of proportions
        #Find out the unique values in the batch list
        #Calculate their proportion using groupby.size()?
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

    


    def assignByPc(self, df, dPc):  # here df is a dataframe with column 
                                    # dPc is the df.groupby(batchField).size() result
                                    # converted into decimilized proportions
        #group = df['group'].iloc[0]
        qCol = dPc.iloc[:,1]
        qCol = list(qCol)
        qCol = [0] + qCol
        cut = pd.qcut(np.arange(df.shape[0]), #Series to be cut by quantiles
                q = np.cumsum(qCol),
                labels = dPc.iloc[:,0]
                ).get_values()

        #Original parameters:
        # q=np.cumsum([0] + proportions[group]), #The quantiles to use
        # labels=range(len(proportions[group])) #Labels for resulting bins

        return pd.Series(cut[np.random.permutation(df.shape[0])],
                                index=df.index,
                                name='assignment')
# 
# To perform the assignment in proportion with group
#   df['assignment'] = df.groupby('group', group_keys=False).apply(assigner)
#   df.head()
# Out[233]:
#    customer_id group  assignment
# 0       0.6547     c           1
# 1       1.4190     a           1
# 2       0.4205     a           0
# 3       2.3266     a           1
# 4      -0.5691     b           0

# to obtain pivot table
# pd.pivot_table(df,index=['Group'],values=["customer_id"],aggfunc=lambda x: len(x.unique()))
# OR
# In [234]: (df.groupby(['group', 'assignment'])
#              .size()
#              .unstack()
#              .assign(proportion=lambda x: x[0] / (x[0] + x[1])))
# Assuming that 0 and 1 are the two batches to assign to
# Out[234]:
# assignment     0     1  proportion
# group
# a           1659  1658      0.5002
# b           1335  2003      0.3999
# c            669  2676      0.200