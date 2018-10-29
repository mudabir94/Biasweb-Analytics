"""
Utility to randomly allocate data by bins, optionally
in proportion to another group level
"""
# Importing the libraries
import numpy as np
import pandas as pd
from tkinter import *
from tkinter.filedialog import askopenfilename

class Assigner:
    def __init__(self, df = None):
        self.df = df

    def assign(self, no_groups, df=None, gpLabels=None):
        """ 
        The function that assigns a DataFrame (df) randomly into a number of groups
        Parameters
        ----------
            no_groups = the number of groups to split the df into
            df = in case a DataFrame other than in initialization is to be split (useful for subgrouping within groups)
            gpLabels = the labels to give, default is 1,2,3...
        Returns
        -------
            An indexed series of the group lables that can be attached to the given df.
        """
        if not isinstance(df, pd.DataFrame):
            df = self.df
        if not gpLabels:
            gpLabels = range(1,no_groups+1)
        buckets = pd.qcut(
                      np.arange(df.shape[0]), #a vector of the indices of the dataframe  
                      q=no_groups,
                      labels=gpLabels #NEEDS TO BE CUSTOMISED SO USER CAN GIVE LABELS
                                          #DEFAULT SHOULD START WITH 1 NOT 0
                    ).get_values()
        buckets = buckets[np.random.permutation(df.shape[0])]
        return pd.Series( buckets, index=df.index)
 
    def splitInBins(self, no_bins, binName, df=None, binLabels=None):
        """
        Similar to assign() but also returns the bins as separate dataframes,
        in a groupby object, and nominates a field name for the bins column
        """
        if not isinstance(df,pd.DataFrame):
            df = self.df
        df[binName] = self.assign(no_groups=no_bins,
                        df=df,
                        gpLabels=binLabels
        )
        groups = df.groupby(binName)
        print(groups.size())
        return df
    
    def splitByField(self, nBins, bName, fieldName, data=None, bLabels=None):
        """
        Applies splitInBins groupwise on a specified field to ensure
        proportions of the field are maintained.
        """
        if not isinstance(data,pd.DataFrame):
            data = self.df
        data = (data.groupby(fieldName)
                .apply(lambda x: 
                    self.splitInBins(
                        no_bins=nBins,
                        binName=bName,
                        df=x,
                        binLabels=bLabels
                    )
                )
        )
        return data

        
        groups = self.df.groupby(fieldName)
        print(groups.size())
        return groups
            
    
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

    def calcSplitRatio(self):
        """
        Input: Series or List of batches
        Output: dictionary of proportions
        Find out the unique values in the batch list
        Calculate their proportion using groupby.size()?
        """
        pass
        
    def getLocalDToAssign(self, fPath = None):
        #from tkinter.filedialog import asksaveasfilename
        if fPath:
        # Read in a file and evaluate its format [Excel or CSV]
            fToUpload = fPath
        else:
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
    
    def extractData(self, fName, shNo = 0):
        """
        Extracts a pandas DataFrame from a given CVS or XLS file
        returns: needShNo = whether we need selection of sheet number
        """
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