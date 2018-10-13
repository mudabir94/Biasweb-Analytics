class Experiment_Admin():

    lastname=''
    user_id=0
    def __init__(self,lastname,userid):  

        self._lastname=lastname
        self._user_id=userid
    def getExperiment_AdminInfo(self):
         
        datadict={'lastname':self._lastname,'user_id':self._user_id}            
        return datadict
    '''    
    def viewExperimentlist(self):
        # select * from experiment
        # get role id
        # select * from experiment where roleid=---
        return 
    def addExperiment(self):
    def delExperiment(self):
    def editExperiment(self):
    '''