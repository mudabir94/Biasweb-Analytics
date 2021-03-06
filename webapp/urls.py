from django.conf.urls import url, include
from django.urls import path
from . import views 
urlpatterns = [
    url(r'^index_ahp/',views.indexAhp, name='index_ahp'),   
   
   
   
    # These urls doesn't have templates. These functions are
    # called  through ajax. They are either used to retrieve  
    # data from model and render the data to some other template.         
    url(r'^hidefeature/',views.hideFeature, name='hidefeature'),                
    url(r'^updatefeatureposition/',views.updateFeaturePosition, name='updatefeatureposition'),                   
    url(r'^showfeature/',views.showFeature, name='showfeature'),                       
    url(r'^globalFunc/',views.globalFunc,name='gf'),      
#----------------------------------------------------------------------------------------------------------    
    # Basic Landing Pages
    # Home Page. base template is base.html
    url(r'^$',views.Home.as_view(),name='homepage'),
    # About Page. base template is base.html

#----------------------------------------------------------------------------------------------------------
    url(r'^admin_setup/' , views.adminSetup.as_view() , name='admin_setup') ,
    url(r'^mobile/',views.mobile_phone_view.as_view(),name='mobileview'),
    path('mobile_info/<int:id>',views.mobile_phone_view.one_mobile_func, name='mobileinfo'),
    url(r'^filter/',views.filter.as_view(), name='filter'),
    
    
    url(r'^comparemobile_specs/',views.compareMobileSpecs, name='comparemobile_specs'),
    url(r'^comparemobilespecsfilt_ver/',views.compareMobileSpecsFilterVer, name='comparemobilespecsfilt_ver'),
    url(r'^filtered_mobile_view/',views.filteredMobileView,name='filtered_mobile_view'),
    url(r'^criteria_weights/',views.criteriaWeights,name='criteria_weights'),
    url(r'^comparemobile_1by1_direct/',views.compareMobileOneByOneDirect,name='comparemobile_1by1_direct'),
    url(r'^comparemobile_2by2_direct/',views.compareMobileTwoByTwoDirect,name='comparemobile_2by2_direct'),
    url(r'^delete_selected_adminphones/',views.deleteSelectedAdminPhones,name='delete_selected_adminphones'),


    url(r'^save_current_subj_exp/',views.SaveCurrentSubjExp, name='save_current_subj_exp'),

    url(r'^showmob/',views.showMob, name='showmobile'),
    url(r'^showScore/',views.showScore, name='showscore'),


    url(r'^importcsv_submit/',views.ImportCsv_submit, name='importcsv_submit'),
    
#-----------------------------------------------------------------------------------------------------
# Experiment admin related links/urls
    url(r'^biastestfeatures/',views.BiasTestFeature.as_view(), name='select_biasfeature'),
    url(r'^manageshortlist/',views.ManageShortList.as_view(), name='manage_shortlisting'),
    url(r'^createexp/',views.createExperiment.as_view(), name='createexp'),
    url(r'^addexpdiscp/',views.createExperiment.addDesp, name='addexpdiscp'),
    url(r'^get_default_f_levels_from_platform_feature/',views.createExperiment.getDefaultFLevelsFromPlatformFeature, name='get_default_f_levels_from_platform_feature'),


    url(r'^manageexp/',views.ManageExperiment.as_view(), name='manageexp'),
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
    url(r'^store_selected_admin_phones/',views.storeSelectedAdminPhones, name='store_selected_admin_phones'),
    url(r'^remove_selected_admin_phones/',views.removeSelectedAdminPhones, name='remove_selected_admin_phones'),
    url(r'^price_range_retrieve/',views.priceRangeRetrieve, name='price_range_retrieve'),
    url(r'^get_selectedadmin_phones/',views.getSelectedAdminPhones, name='get_selectedadmin_phones'),
    url(r'^get_mobile_data/',views.getMobiledata,name='get_mobile_data'),
    url(r'^getReqPhones/',views.getReqPhones,name='getReqPhones'),

    
    url(r'^retspecmobilephone/',views.retSpecMobilePhone, name='retspecmobilephone'),
    url(r'^get_specificmobile_data/',views.getSpecificMobileData,name='get_specificmobile_data'),
    url(r'^savephonesets/',views.SavePhoneSets,name='savephonesets'),
    url(r'^savephonesets_p0/',views.SavePhoneSets_P0,name='savephonesets_p0'),

    url(r'^ordercriteriasetup/' , views.orderCriteria_Setup.as_view() , name='ordercriteriasetup') ,
    url(r'^defaultcriteriasetup/' , views.defaultCriteria_Setup.as_view() , name='defaultcriteriasetup') ,
    url(r'^cr_criteriasetup/' , views.CrCriteriaSetup.as_view() , name='cr_criteriasetup') ,
    url(r'^cr_on_co_on_criteriasetup/' , views.Cr_On_Co_On_CriteriaSetup.as_view() , name='cr_on_co_on_criteriasetup') ,






    
#---------------------------------------------------------------------------------------------   
    ## Pages that are not currently used. 
    #url(r'^blog/', views.blogview.as_view(), name='blog'), 
    url(r'^showfilter/',views.showFilter.as_view(), name='showfilter'),
    #url(r'^$', views.signUp, name='signup'), 

#---------------------------------------------------------------------------------------------
# Temprary...
    url(r'^submit_data/' , views.submitData , name='submit_data') ,
    
    url(r'^createsurveyform/' , views.createSurveyForm.as_view() , name='createsurveyform') ,
    url(r'^retrievesurveyform/' , views.retrieveSurveyForm , name='retrievesurveyform') ,


    url(r'^savesurveyform/' , views.saveSurveyForm.as_view() , name='savesurveyform') ,
    url(r'^get_crit_info/' , views.getCritInfo, name='get_crit_info') ,
    url(r'^savesurveyresult/' , views.saveSurveyResult, name='savesurveyresult') ,

]
