import numpy as np
import pandas as pd
from biasweb.utils.Assigner import Assigner

assigner = Assigner()
#%%TEST ASSIGNMENT ON RANDOMLY ASSEMBLED DB
assigner.assignAutoTest()
#dSubBatches = assigner.splitInBins(3,'batch' )
#dSubBatches.get_group(0).head() #Batch 0 members summary/head
dSub = assigner.df
dSub.groupby('group').size()
#Following operations are simply to make uneven groups to test
#reassignment correction.
dSub.groupby(['batch','group']).size().unstack()
dSub = dSub[dSub.batch != 'C'] #Just keeping two batches
dSub.groupby(['group','batch']).size().unstack()
dSub = dSub[~((dSub.group == 'c') & (dSub.batch == 'A'))] #Making group c unevenly distributed
dSub.groupby(['group','batch']).size().unstack()
#Test block assignment
GpLabel = 'group'
batchesTitle = 'batch'
dfGpCount = dSub.groupby(GpLabel).size().to_frame(name = 'split_edges')
total = dSub.shape[0]
dfGpPc = dfGpCount.apply(lambda x: x / total)
#TODO@SHAZIB: Add Column and then convert to dictionary
dPc = dfGpPc.reset_index()
dPc
dAss = (dSub.groupby(batchesTitle, group_keys=False)
            .apply(assigner.assignByPc, dPc))
dSub[GpLabel] = dAss
dSub.groupby(['assigned','batch']).size().unstack()
