from django.conf.urls import url, include
from django.urls import path
from . import views 
urlpatterns = [
   url(r'^index_ahp/',views.indexAhp, name='index_ahp'),   
   
   
   
    # These urls doesn't have templates. These functions are
    # called  through ajax. They are either used to retrieve  
    # data from model and render the data to some other template.         
    url(r'^test/',views.test, name='test'),                
    url(r'^ind/',views.ind, name='ind'),                   
    url(r'^on/',views.on, name='on'),                       
    url(r'^globalFunc/',views.globalFunc,name='gf'),      
#----------------------------------------------------------------------------------------------------------    
    # Basic Landing Pages
    # Home Page. base template is base.html
    url(r'^$',views.Home.as_view(),name='homepage'),
    # About Page. base template is base.html




#----------------------------------------------------------------------------------------------------------
    url(r'^admin_setup/' , views.adminSetup , name='admin_setup') ,
    url(r'^mobile/',views.mobile_phone_view.as_view(),name='mobileview'),
    path('mobile_info/<int:id>',views.mobile_phone_view.one_mobile_func, name='mobileinfo'),
    url(r'^filter/',views.filter.as_view(), name='filter'),
    
    
    url(r'^comparemobile_specs/',views.compareMobileSpecs, name='comparemobile_specs'),
    url(r'^showmob/',views.showMob, name='showmobile'),
    url(r'^showScore/',views.showScore, name='showscore'),


    url(r'^importcsv_submit/',views.ImportCsv_submit, name='importcsv_submit'),
    
#-----------------------------------------------------------------------------------------------------
# Experiment admin related links/urls
    url(r'^biastestfeatures/',views.BiasTestFeature.as_view(), name='select_biasfeature'),
    url(r'^manageshortlist/',views.ManageShortList.as_view(), name='manage_shortlisting'),
    url(r'^createexp/',views.createExperiment.as_view(), name='createexp'),
    url(r'^subdetails/',views.subDetails, name='subdetails'),
    url(r'^uploadsamplefile/',views.uploadSampleFile, name='uploadsamplefile'),
    url(r'^postexp/',views.postExp, name='postexp'),
    url(r'^import_subjects/',views.importSubjects, name='import_subjects'),
    url(r'^assign_blocks/',views.assignToBlocks, name='assign_blocks'),
    url(r'^selfdefault/',views.selfDefault,  name='selfdefault'),
    url(r'^removesessionobj/',views.removeSessionObj,  name='remove_session_obj'),
    url(r'^deleteallsubjects/',views.deleteAllSubjects,  name='deleteallsubjects'),
    url(r'^get_saved_subject_data_expcont/',views.getSavedSubjectDataExpCont,  name='get_saved_subject_data_expcont'),
    url(r'^import_excel/',views.importExcel,  name='import_excel'),
    url(r'^saveexperiment/',views.saveExperiment,  name='saveexperiment'),
    url(r'^datadefinded/',views.datadefined.as_view(), name='datadefined'),
    url(r'^store_selected_admin_phones/',views.storeSelectedAdminPhones, name='store_selected_admin_phones'),
    
#---------------------------------------------------------------------------------------------   
    ## Pages that are not currently used. 
    #url(r'^blog/', views.blogview.as_view(), name='blog'), 
    #url(r'^showfilter/',views.showFilter.as_view(), name='showfilter'),
    #url(r'^$', views.signUp, name='signup'), 

#---------------------------------------------------------------------------------------------
]
