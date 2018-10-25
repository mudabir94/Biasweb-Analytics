In [228]: df = pd.DataFrame({'customer_id': np.random.normal(size=10000), 
                             'group': np.random.choice(['a', 'b', 'c'], size=10000)})

In [229]: proportions = {'a':[.5,.5], 'b':[.4,.6], 'c':[.2,.8]}

In [230]: df.head()
Out[230]:
   customer_id group
0       0.6547     c
1       1.4190     a
2       0.4205     a
3       2.3266     a
4      -0.5691     b

In [231]: def assigner(gp):
     ...:     group = gp['group'].iloc[0]
     ...:     cut = pd.qcut(
                  np.arange(gp.shape[0]), 
                  q=np.cumsum([0] + proportions[group]), 
                  labels=range(len(proportions[group]))
              ).get_values()
     ...:     return pd.Series(cut[np.random.permutation(gp.shape[0])], index=gp.index, name='assignment')
     ...:

In [232]: df['assignment'] = df.groupby('group', group_keys=False).apply(assigner)

In [233]: df.head()
Out[233]:
   customer_id group  assignment
0       0.6547     c           1
1       1.4190     a           1
2       0.4205     a           0
3       2.3266     a           1
4      -0.5691     b           0

In [234]: (df.groupby(['group', 'assignment'])
             .size()
             .unstack()
             .assign(proportion=lambda x: x[0] / (x[0] + x[1])))
Out[234]:
assignment     0     1  proportion
group
a           1659  1658      0.5002
b           1335  2003      0.3999
c            669  2676      0.2000