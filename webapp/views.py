import codecs
import csv
#-------------------------------------------------------------------------------------------------
#test_experiment imports. 
import itertools
import json
import os
import pickle
from pathlib import Path
#--------------------------------------------------------------------------
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


#--------------------------------------------------------------------------------------------------
from django.core import serializers
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import connection
from django.db.models import Q

#------------------------------------------------------------------------------------------
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

import numpy as np
import pandas as pd
from pandas.compat import StringIO
#--------------------------------------------------------------------------------------
from biasweb.experiment.controller import ExperimentController,SubjCont
from biasweb.pythonscripts.experiment_admin import Experiment_Admin
from biasweb.pythonscripts.getdata import get
# from biasweb.pythonscripts.insertcsvfiletotable import populate_Table
from biasweb.utils.assign import Assigner

#loading forms from forms.py file. 
from .forms import (NameForm, SignUpForm, blogForm, filterform,
                    sort_filter_form)
#-----------------------------------------------------------------
from webapp.models import experiment as Experiment
from .models import experiment as exp

from .models import Role, User, blog
from .models import ( 
                    mobilephones, 
                    platform_feature, 
                    Subject,
                    samsung_phone,
                    sort_feature, 
                    userscoreRecord,
                    ExpCriteriaOrder,
                    PhoneCriteria,
                    experiment_feature,
                    StoreHoverBarChartLogs,
                    StoreHoverPieChartLogs,
                    StoreNextPrevButtonLogs,
                    StoreCritWeightLogs,
                    generalCriteriaData,
                    customExpSessionTable,
                    surveyForm,
                    )


from .models import selectedAdminPhones,criteria_catalog_disp,exStatusCd
from django.views.decorators.cache import never_cache

import datetime
from functools import reduce
import operator
from django.db.models import Max

#--------------------------------------------------------------------------------------------------
role=1   #global variable used in adminsetup and globalFunc function. 
#mobiles=samsung_phone.objects.raw('SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2') # making mobiles object global.
# mobiles=mobilephones.objects.raw('SELECT * FROM webapp_mobilephones WHERE id=1 or id=2') # making mobiles object global.
mobiles=None
filter_flag=None
sizeofmob=0 # global variable assigned in filter class.
filt_mobiles=None
exp_under_test=0
def_featlvl_frm_pf_dict={}
exp_feat_levels=[]
storeuserpagelogs={}
critw_logs_dict={}

#-------------------------------------------------------------------------------------------------

            
@method_decorator(login_required, name='dispatch')

class Home(TemplateView):
    template_name='webapp/home.html'
    def get(self,request):
        global storeuserpagelogs
        storeuserpagelogs={}
        print("storeuserpagelogs---",storeuserpagelogs)
        #userobj= User.objects.values_list('role_id_id',flat=True).filter(id=request.user.id)
        
        #**************************************************
        # This code gets the user id, then on bases of role we will assign the templates.
       
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role=userobj.role_id_id
        roleobj=Role.objects.get(pk=role)
        role=roleobj.role_name
        print(role)

        if role=='Super_Admin':
            
            template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
            template_main_homepage="webapp/main_content_temps/homepage_main/superadmin_hp.html"
            data={
                'role_id':userobj.role_id_id,
                'template_sidebar':template_sidebar,
                'template_main_homepage':template_main_homepage,
            }

            # return redirect('/filtered_mobile_view')
            # return render(request,'webapp/2by2comparemobilespecs.html')
            # return render(request,template_sidebar)
        elif role=='Experiment_Admin':
            # roleobj=Role.objects.get(pk=role)
            # role_name=roleobj.role_name
            # print(role_name)
            template_sidebar='webapp/sidebartemplates/sidebartemp_expadm.html'
            template_main_homepage="webapp/main_content_temps/homepage_main/experimentadmin_hp.html"
            data={
                'role_id':userobj.role_id_id,
                'template_sidebar':template_sidebar,
                'template_main_homepage':template_main_homepage,
            }

            
        elif role=='Platform_Admin':
            roleobj=Role.objects.get(pk=role)
            role_name=roleobj.role_name
            print(role_name)
            template_sidebar='webapp/sidebartemplates/sidebartemp_pltfadm.html'
            template_main_homepage="webapp/main_content_temps/homepage_main/platformadmin_hp.html"
            data={
                'role_id':userobj.role_id_id,
                'template_sidebar':template_sidebar,
                'template_main_homepage':template_main_homepage,
            }

        elif role=='Subject':
            # all other conditions of subjects will be done here. 
            # Checking the experiments assigned to the Subjects. 
            exp_list = userobj.subject_set.values_list('exp', flat=True) 
            # Getting the status codes that are active.
            # exStatusCd_list=exStatusCd.objects.filter(status_code__gte=11)
            exStatusCd_list=exStatusCd.objects.filter(status_code__gte=11)

            # Fetching that the experiments who has status code as active for the user/subject. 
            inner_qs = exp.objects.filter(id__in=list(exp_list),status_code__in=exStatusCd_list)
            # Using the experiment list for display
            print("inner_qs",inner_qs)
            print("inner_qs",list(inner_qs.values('id')))
            explist=inner_qs.values('id')
            print("explst",list(explist))
            # Now we know how many experiments the subject is invovled. 
            # For now we'll hard code to get one subject having one active exp... 
            # I have changed from hard coded id to get the exp obj based on first active experiment. 
            exp_obj=exp.objects.get(id=list(inner_qs.values('id'))[0]['id'])
            Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
            print(Sub_obj.block)
            exp_chosenlevel=list(experiment_feature.objects.filter(used_in=exp_obj).values_list('chosen_levels',flat=True))
            exp_defaultlevel=list(experiment_feature.objects.filter(used_in=exp_obj).values_list('default_levels',flat=True))
            exp_chosenlevel_list=[]
            exp_defaultlevel_list=[]
            global exp_feat_levels
            exp_feat_levels=[]
            print("Blocks",Sub_obj.block.levels_set)
            print("CHOSEN LEVELS",exp_chosenlevel)
            print("Default LEVELS",exp_defaultlevel)
            exp_chosenlevel=['' if v is None else v for v in exp_chosenlevel]
            exp_defaultlevel=['' if v is None else v for v in exp_defaultlevel]

            for blk in Sub_obj.block.levels_set:
                for chlevl in exp_chosenlevel:
                    if blk in chlevl:
                        print("FOund")
                        index=exp_chosenlevel.index(chlevl)
                        exp_chosenlevel[index]=blk
            print("CHOSEN LEVELS",exp_chosenlevel)
            for i in exp_chosenlevel:
                if i:
                    
                    exp_chosenlevel_list.append(i)
                    exp_feat_levels.append(i)
            for i in exp_defaultlevel:
                if i:
                    print(i)
                    exp_defaultlevel_list.append(i[0])
                    exp_feat_levels.append(i[0])
            print("exp_feat_levels",exp_feat_levels)


            








            template_sidebar='webapp/sidebartemplates/sidebartemp_subject.html'
            template_main_homepage="webapp/main_content_temps/homepage_main/subject_hp.html"
            data={
                'role_id':userobj.role_id_id,
                'template_sidebar':template_sidebar,
                'template_main_homepage':template_main_homepage,
                'explist':explist,
                "exp_id":exp_obj.id
            }
        #*****************************************************
        return render(request,self.template_name,data)
    def post(self,request):
        return render(request,self.template_name)
# IT IS NOT USED ANYWHERE
def indexAhp(request):
    return render (request,'webapp/index-ahp.html')
# priceRangeRetrieve
def priceRangeRetrieve(request):
    if request.method=="POST":
        if request.is_ajax:
            price_range_values = request.POST.get('price_range_values')
            price_range_values = json.loads(price_range_values)
            print('price_range_values',price_range_values[0])
            print('price_range_values1',price_range_values[1])

            # mobiles_retrieved=samsung_phone.objects.filter(price_in_pkr__range=(price_range_values[0], price_range_values[1]))
            mobiles_retrieved=mobilephones.objects.filter(price_in_pkr__range=(price_range_values[0], price_range_values[1]))
            print(mobiles_retrieved) 
            mobiles_retrieved = list(mobiles_retrieved.values())
            
            
            # for att in dir(mobiles_retrieved):
            #     print (att, getattr(mobiles_retrieved,att))
            data={
                # 'samsung_phones': mobiles_retrieved
                'mobilephones':mobiles_retrieved
            }
            return JsonResponse(data)

def showScore(request):
    mobileid=0
    featname=""
    elementid=0
    featpriority=0 
    userid=0
    columnId=0

    if request.method=="POST":
        if request.is_ajax:
            d = request.POST.get('d')
            b = json.loads(d)
             
            print("lenght",len(b))
           
            for dic in b: # getting single index of the models dictionary  that is passed through ajax.
                for k in dic:
                    print(k,dic[k]) # name and value of that specific instance. 
                    if (k=="mid"):
                        mobileid=dic[k]
                    elif (k=="mfeat"):
                        featname=dic[k]
                    elif (k=="userid"):
                        userid=dic[k]
                    elif(k=="elementid"):
                        elementid=dic[k]
                    elif(k=="columnId"):
                        columnId=dic[k]
                    elif(k=="featprior"):
                        featpriority=dic[k]
                    else:
                        print("do nothing")
                print(featname,featpriority,mobileid,userid,elementid,columnId)
                p = userscoreRecord(column_id=columnId,element_id=elementid,feat_priority=featpriority,feat_name=featname,mobile_id=mobileid,user_id=userid,date_created=timezone.now(), date_modified=timezone.now())
                # print("p",p)
                p.save()

    
        #Get all values of each index of the dictionary then store the info into the table. 
        # Fetch info for the current user. Get the info and make calculations and generate a score.
        # Send all the score  through ajax to the page. 
            
            print("jk",request.user.id)
            print("jk",request.user.username)
            dict = {'mobiles':'mobile info'}
            
    return HttpResponse(json.dumps(dict), content_type='application/json')
def storeSelectedAdminPhones(request):
    expCont = getExpController(request)
    print('expContid',expCont.idField)
    print('user_id',request.user.id)
    if request.method == 'POST':
        if request.is_ajax:
            mobiledata = request.POST.get('mobiledata')
            custom_exp_id = request.POST.get('custom_exp_id')

            mobiledata_json = json.loads(mobiledata)
            print('custom_exp_id',custom_exp_id)
            mobiledata_json=int(mobiledata_json)

           
            userobj=User.objects.get(pk=request.user.id)

            expobj=exp.objects.get(custom_exp_id=custom_exp_id)
            



            # smgphone=samsung_phone.objects.get(pk=mobiledata_json)
            # selphones=selectedAdminPhones(user=userobj,exp=expobj,mob=smgphone)
            phones=mobilephones.objects.get(pk=mobiledata_json)
            print("sel_phones",phones)
            cellphones=selectedAdminPhones.objects.filter(user=userobj,exp=expobj,mob=phones)
            print(cellphones)
            # a check to see if the phone is already selected for the same exp. 
            if not cellphones:
                cellphones=selectedAdminPhones(user=userobj,exp=expobj,mob=phones)
                
                cellphones.save()
                data={'data':'Successfully inserted in model'}
            else:
                data={'data':'phone already exsists in the same experiment'}
            return JsonResponse(data)
def removeSelectedAdminPhones(request):
    if request.method=='POST':
        if request.is_ajax():
            mobiledata=request.POST.get('mobiledata')
            custom_exp_id = request.POST.get('custom_exp_id')
            print("custom_exp_id",custom_exp_id)
            mobiledata_json=json.loads(mobiledata)
            mobiledata_json=int(mobiledata_json)

            
            expobj=exp.objects.get(custom_exp_id=custom_exp_id)
            phones=mobilephones.objects.get(pk=mobiledata_json)
            
            

            cellphones=selectedAdminPhones.objects.filter(exp=expobj,mob=phones)
            
            cellphones.delete()
            return JsonResponse({'data':'Successfully remved from model'})

comp_mobiles=''    
def getSelectedAdminPhones(request):
    if request.method=='GET':
        if request.is_ajax():

            expCont = getExpController(request)
            existExpId = expCont.exp.id
            # print("existExpId",existExpId)
            expobj=exp.objects.get(custom_exp_id=existExpId)
            # print("expobj",expobj)
            ## A Check is to be set for knowing if the admin has created new, working on existing or have not created the exp obj yet. 
            # if working on existing:
           
            cellphones=selectedAdminPhones.objects.filter(exp=expobj)

            clist=[]
            for c in cellphones:
                print("mid",c.mob_id)
                clist.append(c.mob_id)
            phones=mobilephones.objects.filter(id__in=clist)

            cellphones = list(phones.values())
            # samsung_phones=mobiles_retrieved
            cellphones_str=cellphones
            print("cellphones_str",cellphones_str)
        
            return JsonResponse(
            {  
                # 'samsung_phones':samsung_phones
                'cellphones':cellphones_str,
                'data':'retrieved data from model'
            })


# It gets the phones id list and use the ids to exctract from mobilephones model. 
# through which we extract size(length/Number) of mobiles and store in a global variable.
# Last thing is to send exp_feat_levels list back to the page in sucess function. 
def showMob(request):
    if request.method=="POST":
        if request.is_ajax:
            mobiledata = request.POST.get('mobiledata')
            mobiledata_json = json.loads(mobiledata)
            print("mobiledata_json",mobiledata_json[0])
            query_array=[]
            count=1    
            for key,value in  enumerate(mobiledata_json):
                print("key",key)
                print ("val", value)
                query_array.append(value)
            query=mobilephones.objects.filter(id__in=(query_array))
          
            global comp_mobiles
            global sizeofmob
            global exp_under_test
                
            comp_mobiles=query
            size_of_mobile=len(list(comp_mobiles))
            sizeofmob=size_of_mobile
            print(comp_mobiles)

            
            dict = {'size_of_mobile':size_of_mobile}
            print("Uer Id",request.user.id)
            userobj=User.objects.get(pk=request.user.id)

            exp_obj=exp.objects.get(id=exp_under_test)
            Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
            print("Sub_obj",Sub_obj)
           

            global exp_feat_levels

            data={
                # 'dict':json.dumps(dict),
                'subject_block':exp_feat_levels,

                # 'subject_block':exp_feat_levels,
                'data':"success",
            }

    return JsonResponse(data)
    #return render_to_response(request,'webapp/showmob.html',{'mobiles':mobiles}) 
    '''
    query = 'SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2'
    mobiles=samsung_phone.objects.raw(query)
    print(mobiles)
    return render(request,'webapp/showmob.html',{'mobiles':mobiles})
    '''
crit_list=[]
criteria_weights_dict={}
allmobile=[]
numofmobiles=[]
criteria_list=[]
alternative_list=[]


# Functionilty--
# Two Methods.. 
# Get and Post
# GET Called when the page is loaded for first time or without ajax call. 
#  If this is called for the first time, it'll store the page in logs storeuserpagelogs'
    # Will Check Criteria Display Method and Alternatives Display Method and Revisablity Features
    # Based on C. Feature criteria list will be exctracted from the tables that was selected by admin
    # and will send to criteria_weights.html page. 
# else 
# Post is called through ajax request when we want to save the changes made by the user.
# It saves the criterias values that are set by the user. 
# The logs as well.  

def criteriaWeights(request):
    global crit_list
    global criteria_weights_dict
    global exp_feat_levels
    global exp_under_test
    global critw_logs_dict
    # No check if block is CDM (C.Full and C.Prune... )

    template_name='webapp/criteriaweights.html'
   
    if request.method=="GET":
        print("storeuserpagelogs",storeuserpagelogs)

        if "criteriaweights" in storeuserpagelogs:
            flag="true"
       
            adm = [idx for idx in exp_feat_levels if idx.startswith("A.")] 
            # if revisabilty is on then pagevisited should be false. 
             
            reviseability = [idx for idx in exp_feat_levels if idx.startswith("R.")] 
            print("res -- R",reviseability[0])
            crit_list=[]
            if reviseability[0]=="R.1":
                crit = [idx for idx in exp_feat_levels if idx.startswith("C.")] 
                crit=crit[0].lower()
                exp_obj=exp.objects.get(id=exp_under_test)
                ExpCriteria_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,cOrder_id=crit)
                print("ExpCriteria_obj",ExpCriteria_obj)
                crit_list_obj=ExpCriteria_obj.values_list('pCriteria__criteria_name',flat=True)
                print("crit_list_obj",crit_list_obj)
                crit_list=list(crit_list_obj)
                crit_list.insert(0,"imagepath1")
                crit_list.append("Others")
                flag="false"

            data={
                'crit_list':crit_list,
                "ADM":adm[0],
                "pagevisited":flag,
                'userid':request.user.id,
                }
            return render(request,template_name,data)
        else:
            flag="false"
            storeuserpagelogs["criteriaweights"]=[datetime.datetime.now(),exp_under_test,request.user.id]

            print("NOT AJAX CRITERIA WIETNGTS")
            # get the criterias set by admin for the exp... 
            # check if c.full or c.prune in res1
            print("exp_feat_levels",exp_feat_levels)
            
            res = [idx for idx in exp_feat_levels if idx.startswith("C.")] 
            res=res[0].lower()
            exp_obj=exp.objects.get(id=exp_under_test)
            ExpCriteria_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,cOrder_id=res)
            print("ExpCriteria_obj",ExpCriteria_obj)
            crit_list_obj=ExpCriteria_obj.values_list('pCriteria__criteria_name',flat=True)
            print("crit_list_obj",crit_list_obj)
            crit_list=[]
            crit_list=list(crit_list_obj)
            crit_list.insert(0,"imagepath1")
            crit_list.append("Others")
            userobj=User.objects.get(pk=request.user.id)
            print("exp_under_test",exp_under_test)
            exp_obj=exp.objects.get(id=exp_under_test)
            Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
            print("blocks",Sub_obj.block.levels_set)
            print("exp_feat_levels",exp_feat_levels)
            # res1 = [idx for idx in Sub_obj.block.levels_set if idx.startswith("A.")] 
            adm = [idx for idx in exp_feat_levels if idx.startswith("A.")] 
            print("adm",adm)

            data={
                'crit_list':crit_list,
                "ADM":adm[0],
                'userid':request.user.id,
                "pagevisited":flag,

                
            }
            return render(request,template_name,data)
    elif request.method=="POST":
        if request.is_ajax:
            critlist_val_dict = request.POST.get('critlist_val_dict')
            critlist_val_dict = json.loads(critlist_val_dict)
            critw_logs_dict = request.POST.get('critw_logs_dict')
            critw_logs_dict = json.loads(critw_logs_dict)
            
            print("critlist_val_dict",critlist_val_dict)
            criteria_weights_dict=critlist_val_dict
            print("criteria_weights_dict",criteria_weights_dict)
            data={}
            return JsonResponse(data) 
# When the page is loaded  both of its GET and POST functions are called respectively through ajax. 
# GET Method send back Interactivity and Revisiablity features. 
# POST Methond sends back  multiple list and dict needed to populate the page. 
def compareMobileOneByOneDirect(request):
    template_name='webapp/comparemobile1by1direct.html'
      
    global crit_list
    global comp_mobiles
    global catalogcrit_show_list
    global criteria_weights_dict
    global exp_under_test
    global exp_feat_levels


    if request.method=="GET":
            

        if request.is_ajax():

            userobj=User.objects.get(pk=request.user.id)
            exp_obj=exp.objects.get(id=exp_under_test)
            Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
            print("blocks",Sub_obj.block.levels_set)
            interactivity = [idx for idx in exp_feat_levels if idx.startswith("I.")] 
            print("res -- I",interactivity[0])
            
            reviseability = [idx for idx in exp_feat_levels if idx.startswith("R.")] 
            print("res -- R",reviseability[0])
            storeuserpagelogs["comparemobile1by1direct"]=[datetime.datetime.now(),exp_under_test,request.user.id]

            data={
                'userid':request.user.id,
                "interactivity_data":interactivity[0],
                "reviseability_data":reviseability[0]
            }
            return JsonResponse(data)
        else:
            # userobj=User.objects.get(pk=request.user.id)
            # exp_obj=exp.objects.get(id=exp_under_test)
            # Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
            
            data={}
            return render(request,template_name,data)

    elif request.method=="POST":
        print("criteria_weights_dict",criteria_weights_dict)
        print("POSSSST")
        mobile={}
        allmobile={}
        alternative_list=[]
        data={}
        criteria_list=[]
    
        # criteria_list=['imagepath1']
        print("crit_list",crit_list)

        if crit_list:
            for crit in crit_list:
                criteria_list.append(crit)
        else:
            crit = [idx for idx in exp_feat_levels if idx.startswith("C.")] 
            crit=crit[0].lower()
            exp_obj=exp.objects.get(id=exp_under_test)
            ExpCriteria_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,cOrder_id=crit)
            print("ExpCriteria_obj",ExpCriteria_obj)
            crit_list_obj=ExpCriteria_obj.values_list('pCriteria__criteria_name',flat=True)
            print("crit_list_obj",crit_list_obj)
            crit_list=list(crit_list_obj)
            crit_list.insert(0,"imagepath1")
            crit_list.append("Others")
            for crit in crit_list:
                criteria_list.append(crit)

        test_mobiles = comp_mobiles
        for m in test_mobiles:
            print('m objest',m)
            for crit in criteria_list:
                if (crit!="Others"):
                    print("crit",crit)
                    print(getattr(m, crit))
                    print("M",m)
                    mobile[crit]=getattr(m, crit)

            mobile['Others']=m.Mobile_Name
            print("MOBILE")
            print(mobile)
            alternative_list.append(m.Mobile_Name)
            allmobile[m.Mobile_Name]=mobile

            print("criteria_list",criteria_list)
            numofmobiles=len(allmobile)
            mobile={}
            print("alternative_list",alternative_list)
            # features=['price','resolution','size']
            data={
                'allmobiles':allmobile,
                'numofmobiles':numofmobiles,
                'criteria_list':criteria_list,
                'alternative_list':alternative_list,
                "criteria_weights_dict":json.dumps(criteria_weights_dict)
            }
        return JsonResponse(data)

def compareMobileTwoByTwoDirect(request):
    # global crit_list
    # global comp_mobiles
    # global catalogcrit_show_list
    # global criteria_weights_dict
    global exp_under_test
    template_name='webapp/comparemobile2by2direct.html'
    if request.method=="GET":
        if request.is_ajax():
            userobj=User.objects.get(pk=request.user.id)
            exp_obj=exp.objects.get(id=exp_under_test)
            Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
            print("blocks",Sub_obj.block.levels_set)
            global exp_feat_levels
            interactivity = [idx for idx in exp_feat_levels if idx.startswith("I.")] 
            print("res -- I",interactivity[0])
            
            reviseability = [idx for idx in exp_feat_levels if idx.startswith("R.")] 
            print("res -- R",reviseability[0])
         
            data={
                "interactivity_data":interactivity[0],
                "reviseability_data":reviseability[0]
            }
            return JsonResponse(data)
        else:
            data={}
            return render(request,template_name,data)
    elif request.method=="POST":
        print("criteria_weights_dict",criteria_weights_dict)
        mobile={}
        allmobile={}
        alternative_list=[]
        data={}
        criteria_list=[]
        print("crit_list",crit_list)

        if crit_list:
            for crit in crit_list:
                criteria_list.append(crit)
        test_mobiles = comp_mobiles
        for m in test_mobiles:
            print('m objest',m)
            for crit in criteria_list:
                if (crit!="Others"):
                    print("crit",crit)
                    print(getattr(m, crit))
                    print("M",m)
                    mobile[crit]=getattr(m, crit)

            mobile['Others']=m.Mobile_Name
            print("MOBILE")
            print(mobile)
            alternative_list.append(m.Mobile_Name)
            allmobile[m.Mobile_Name]=mobile

            print("criteria_list",criteria_list)
            numofmobiles=len(allmobile)
            mobile={}
            print("alternative_list",alternative_list)
            # features=['price','resolution','size']
            data={
                'allmobiles':allmobile,
                'numofmobiles':numofmobiles,
                'criteria_list':criteria_list,
                'alternative_list':alternative_list,
                "criteria_weights_dict":json.dumps(criteria_weights_dict)
            }
        return JsonResponse(data)

def compareMobileSpecsFilterVer(request):
    if request.method=="GET":
        
        
        return render(request,'webapp/2by2comapremobilespecsfiltver.html')
    if request.method=="POST":
       
        if request.is_ajax: 
            survey_obj=surveyForm.objects.get(exp=expobj)
            # survey_obj=surveyForm.objects.get(id=2)
            surveydata=survey_obj.surveydata

            mobile={}
            allmobile={}
            
            global comp_mobiles
            global exp_under_test
            exp_obj=exp.objects.get(id=exp_under_test)
            # survey_obj=surveyForm.objects.get(exp=expobj)
            survey_obj=surveyForm.objects.get(id=2)
            surveydata=survey_obj.surveydata

            alternative_list=[]
            crit_check = [idx for idx in exp_feat_levels if idx.startswith("C.")] 
            crit_check=crit_check[0].lower()
            ExpCriteria_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,cOrder_id=crit_check)
            print("ExpCriteria_obj",ExpCriteria_obj)
            crit_list=ExpCriteria_obj.values_list('pCriteria__criteria_name',flat=True)
            crit_list=list(crit_list)
            criteria_list=['imagepath1']
            
           
            interactivity = [idx for idx in exp_feat_levels if idx.startswith("I.")] 
            print("res -- I",interactivity[0])
            
            reviseability = [idx for idx in exp_feat_levels if idx.startswith("R.")] 
            print("res -- R",reviseability[0])
         
            # if catalogcrit_show_list:
            #     for crit in catalogcrit_show_list:
            #         criteria_list.append(crit)
            if crit_list:
                for crit in crit_list:
                    criteria_list.append(crit)
            test_mobiles = comp_mobiles
            print("crit_list",criteria_list)
            for m in test_mobiles:
                print('m objest',m)
                for crit in criteria_list:
                    print(crit)
                    mobile[crit]=getattr(m, crit)
                mobile['Others']=m.Mobile_Name
                print("Mobile ",mobile)

                alternative_list.append(m.Mobile_Name)
                allmobile[m.Mobile_Name]=mobile
                # print(allmobile)
                numofmobiles=len(allmobile)
                mobile={}
                print("alternative_list",alternative_list)
                # features=['price','resolution','size']
                if "2by2comapremobilespecsfiltver" in storeuserpagelogs:
                    flag="true"
                else:
                    flag="false"

                    storeuserpagelogs["2by2comapremobilespecsfiltver"]=[datetime.datetime.now(),exp_under_test,request.user.id]

                data={
                    'userid':request.user.id,
                    "pagevisited":flag,
                    'allmobiles':allmobile,
                    'numofmobiles':numofmobiles,
                    'criteria_list':criteria_list,
                    'alternative_list':alternative_list,
                    'interactivity':interactivity[0],
                    "reviseability":reviseability[0],
                    "surveydata":surveydata,
                }
            # code returns on this one. 
            # if allmobile:
            return JsonResponse(data)

     
def compareMobileSpecs(request):
    

    if request.method=="POST":

        if request.is_ajax: 
            mobile={}
            allmobile={}
            # 
            alternative_list=[]
            criteria_list=['imagepath1','price',"Resolution"]
            # "back_camera","Resolution","battery","price_in_usd",
            # "rating","Weight","Gpu","Dimensions","Cpu"]
             
            # "battery","back_camera",
            # "Resolution"]
            #@TODO: Create test for feature level if c.pruned. Then add other to the criteria list. 
            # for m in mobiles:
            print('user id',request.user.id)
            exp_obj=Experiment.objects.get(custom_exp_id="ses-007-0268")

        
            test_obj=selectedAdminPhones.objects.filter(user=request.user.id,exp=exp_obj,pset_id="P.1")
            print('test_obj')
            test_list=[]
            for tb in test_obj:
                print(tb.mob.id)
                test_list.append(tb.mob.id)
            # test_mobiles = samsung_phone.objects.filter(id__in=test_list)
            test_mobiles = mobilephones.objects.filter(id__in=test_list)
            
            for m in test_mobiles:
                print('m objest',m)
                for crit in criteria_list:
                    print(crit)
                    mobile[crit]=getattr(m, crit)
                mobile['Others']=m.Mobile_Name


                # mobile['imagepath1']=getattr(m,criteria_list[0])
                # mobile['price_in_pkr']=getattr(m,criteria_list[1])
               

                # mobile['imagepath1']=m.imagepath1
                # mobile['price']=m.price_in_pkr
                # print(mobile)
                alternative_list.append(m.Mobile_Name)
                allmobile[m.Mobile_Name]=mobile
                # print(allmobile)
                numofmobiles=len(allmobile)
                mobile={}
                print("alternative_list",alternative_list)
                # features=['price','resolution','size']
                data={
                    'allmobiles':allmobile,
                    'numofmobiles':numofmobiles,
                    'criteria_list':criteria_list,
                    'alternative_list':alternative_list
                }
            # code returns on this one. 
            if allmobile:
                return JsonResponse(data)
    

        

    
    
    # if one by one then load compareMobileSpecs. 
    # if 2 by 2 than totally differnt page. based on permissions. 
    # permissions such as ahp or direct. 
    # interactivity on or off.
    #  
    # template 2by2 compareMobileSpecs display.
    # for 2 by 2 load 2by2compareMobileSpecs html. 
    
    # this is not working.. 
    return render(request,'webapp/2by2comparemobilespecs.html',{
        'mobiles':mobiles,
        's':sizeofmob
        })
def updateFeaturePosition(request):
   
    if request.is_ajax:
       # print("ajax",request.POST.get('data'))
        ####print("PST",request.POST.get('d')) 
        d = request.POST.get('d')
       ### print('JSONLOADS',eval(d))
        b = json.loads(d)

        print(b[0])
        count=1
        # ExpCriteriaOrder_obj=ExpCriteriaOrder.objects.get(pCriteria="cpu")
        # ExpCriteriaOrder_obj.position=3
        # ExpCriteriaOrder_obj.save()
        for key,value in  enumerate(b):
            print(key)
            k=str(int(key)+1)
            print ("test", value,k)
            ExpCriteriaOrder_obj=ExpCriteriaOrder.objects.get(pCriteria=value)
            ExpCriteriaOrder_obj.position=count
            ExpCriteriaOrder_obj.save()
            
            sort_feature_selected_obj=sort_feature.objects.get(feature=value,roles=1)
            sort_feature_selected_obj.position=count
            sort_feature_selected_obj.save()
            
        #     with connection.cursor() as cursor:
        #         cursor.execute("UPDATE webapp_sort_feature SET position="+str(count)+" WHERE feature='"+value+"' and roles="+str(role)+";") 
        #         print("executed") 
            count=count+1

        # not in use
        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
        
        #print ("test", d['color'])
        return render(request, 'webapp/admin_setup.html')

def hideFeature(request):
   
    if request.is_ajax:
       # print("ajax",request.POST.get('data'))
        ####print("PST",request.POST.get('d')) 
        d = request.POST.get('d')
       ### print('JSONLOADS',eval(d))
        b = json.loads(d)

        print(b[0])
        count=1
        
        for key,value in  enumerate(b):
        #   I have to make the roles part dynamic. 
            print ("val", value)
            sort_feature_selected_obj=sort_feature.objects.get(feature=value,roles=1)
            print("sortf",sort_feature_selected_obj) 
            sort_feature_selected_obj.sh_hd=0
            sort_feature_selected_obj.save()
            # with connection.cursor() as cursor:
            #     cursor.execute("UPDATE webapp_sort_feature SET sh_hd="+"0"+" WHERE feature='"+value+"' and roles="+str(1)+"; ") 
            #     print("executed") 
            
        

        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
            
        #print ("test", d['color'])
        return render(request, 'webapp/admin_setup.html')
    
def showFeature(request):
    print("showFeature")
    if request.is_ajax:
       # print("ajax",request.POST.get('data'))
        ####print("PST",request.POST.get('d')) 
        d = request.POST.get('d')
       ### print('JSONLOADS',eval(d))
        b = json.loads(d)

        print(b[0])
        count=1
        
        for key,value in  enumerate(b):
           
            print ("val", value)
            sort_feature_selected_obj=sort_feature.objects.get(feature=value,roles=1)
            print("sortf",sort_feature_selected_obj) 
            sort_feature_selected_obj.sh_hd=1
            sort_feature_selected_obj.save() 
            # with connection.cursor() as cursor:
            #     cursor.execute("UPDATE webapp_sort_feature SET sh_hd="+"1"+" WHERE feature='"+value+"' and roles="+str(role)+" ; ") 
            #     print("executed") 
            
        

        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
            
        #print ("test", d['color'])
        return render(request, 'webapp/admin_setup.html')
  
    
def globalFunc(request):
   
    if request.is_ajax:
        #print("ajax",request.POST.get('data'))
        ####print("PST",request.POST.get('d')) 
        # setnum = request.POST.get('set')
        # ### print('JSONLOADS',eval(d))
        # set_num = json.loads(setnum)
        global feature_to_display
        global feature_to_hide
        role_name=['']
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        print(role)
        feature_to_display=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role_id).order_by('position')
                
        print("feature-->",feature_to_display)
        feature_to_hide=sort_feature.objects.filter(Q(sh_hd = 0),roles=role_id).order_by('position')    
        print("feature2-->",feature_to_hide)
        feature_to_display=list(feature_to_display.values())

        feature_to_hide = list(feature_to_hide.values())

        # print("in func",b)
        # print(type(b))
    

        

        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
            
        #print ("test", d['color'])
        data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide
            }
        return JsonResponse(data)
          
        # return render(request, 'webapp/admin_setup.html',{'role_name':'role','feature_to_display':feature_to_display,'feature_to_hide':feature_to_hide})
#* Variable for features to display and hide.  *#
feature_to_display=''
feature_to_hide=''
class defaultCriteria_Setup(TemplateView):
    def get(self,request):
        flag="true"
        role_name=['']
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        if  request.is_ajax():
           
            # A new check exp controller is made to only see if the exp 
            # exsists or not. if it exsists return its data other wise 
            # return none .
            expCont = checkExpController(request)
            print("EXPCONTSS",expCont)
            if expCont:
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
            else:
                existCusId=""

            # try:
            #     exp_obj=Experiment.objects.get(custom_exp_id=existCusId)            
            #     print("exp_obj",exp_obj)
            #     if (ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains="default").exists()):
            #         ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,cOrder_id__icontains="default",pCriteria_id__status="default",pCriteria_id__priority="mendatory").order_by("id")
            #         mandatory=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #         print("Man",mandatory)
            #         # print("ExpCrtOrd",ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #         ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=0,cOrder_id__icontains="default",pCriteria_id__status="default").order_by("id")
            #         feature_to_hide=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #         # feature_to_hide = [item[0] for item in feature_to_hide]
            #         print("hide",feature_to_hide)
            #         ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,cOrder_id__icontains="default",pCriteria_id__status="default").order_by("id")
            #         feature_to_display=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name","position"))
            #         feature_to_display = [item[0] for item in feature_to_display]
            #         print("display",feature_to_display)
            #         flag="true"
            #     else:
            #         print("Default Else")

            #         feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('id')
            #         mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            #         feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('id')
            #         # feature_to_display = list(feature_to_display.values())
            #         feature_to_display =  list(feature_to_display.values_list("criteria_name","position"))
            #         feature_to_display = [item[0] for item in feature_to_display]
            #         print("feature_to_display--",feature_to_display)
            #         print("feature_mand",mandatory)
            #         feature_to_hide=list()
            #         flag="true"
            # except:
            print("Default Exception")
            feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('position')
            mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('position')
            # feature_to_display = list(feature_to_display.values())
            feature_to_display =  list(feature_to_display.values_list("criteria_name","position"))
            feature_to_display = [item[0] for item in feature_to_display]
            print("feature_to_display--",feature_to_display)
            print("feature_mand",mandatory)
            feature_to_hide=list()
            flag="true"

           
            print("feature",feature_to_display)
            print("feature_to hide",feature_to_hide)
            print("mandatory",mandatory)
            data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide,
                'mandatory':mandatory,
                'flag':flag
            }
            return JsonResponse(data)
    def post(self,request):
        if request.is_ajax:
                default_crit_show_dict = request.POST.get('default_crit_show_dict')
                default_crit_show_dict= json.loads(default_crit_show_dict)
                default_crit_hide_dict = request.POST.get('default_crit_hide_dict')
                default_crit_hide_dict= json.loads(default_crit_hide_dict)
                featlevels_dic=request.POST.get('featlevels_dic')
                postedFLevels = json.loads(featlevels_dic)
                cataloglist=request.POST.get('cataloglist')
                cataloglist = json.loads(cataloglist)
                criteria_catalog_disp.objects.filter(id=1).update(catalog_crit_display_order=cataloglist)
                # global catalogcrit_show_list

                # catalogcrit_show_list=cataloglist
                print("postedFLevels",postedFLevels)
                print("default_crit_show_dict",default_crit_show_dict)
                print("default_crit_hide_dict",default_crit_hide_dict)
                final_def_blocks_to_send = request.POST.get('final_def_blocks_to_send')
                postedDefFLevels=json.loads(final_def_blocks_to_send)
                print("final_def_blocks_to_send",final_def_blocks_to_send)
                
                expCont = getExpController(request)
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
              

                
                # thats it. 
                if postedFLevels:
                    expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                    block_set = expCont.generateBlocks()
                    block_list = list(block_set.all().values('serial_no','levels_set'))
                    print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                else:
                    block_list=""
                print("block_list",block_list)

                #  1st check to see if postedDefFLevels exsists. 
                # if it does then 
                if postedDefFLevels:
                # call expCont.setDefFSet(newDefFLevels=postedDefFLevels,prompt=False)
                    expCont.setDefFSet(newDefFLevels=postedDefFLevels,prompt=False)
                    
                # save orderset Details in expCriteriaOrder
                # Check to see if the exp obj already exists in the table. if it does then we need to update position and show_hide prop of  the rows containing the exp id. 
                # 1. based on the exp obj check if exp exists. if it does then 
                # 2. With the help of dict see the criteria_name, and fetch that row and update it the new position, sh_hd
                exp_obj=Experiment.objects.get(custom_exp_id=existCusId)
                if (ExpCriteriaOrder.objects.filter(exp=exp_obj).exists()):
                    ECO_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj)
                    ECO_obj.delete()
                else:
                    pass
                print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
                p_levList=list()

                for key,s in default_crit_show_dict.items():
                        print(key,":",s)
                        p_levList.append('Def.'+str(key))
                        for count, i in enumerate(s):
                            print("count",count)
                            print("ii",i)
                            
                            try:
                                pCObj=PhoneCriteria.objects.get(criteria_name=i)
                                expOSets=ExpCriteriaOrder()
                                expOSets.exp=expCont.exp
                                expOSets.cOrder_id=key
                                expOSets.pCriteria=pCObj
                                expOSets.fvp="Default"
                                expOSets.position=count+1
                                expOSets.sh_hd=1
                                expOSets.save()
                            except (PhoneCriteria.DoesNotExist):
                                pass
                for key,s in default_crit_hide_dict.items():
                        print(key,":",s)
                        p_levList.append('Def.'+str(key))
                        for count, i in enumerate(s):
                            try:
                                print("count",count)
                                print("ii",i)
                                pCObj=PhoneCriteria.objects.get(criteria_name=i)
                                expOSets=ExpCriteriaOrder()
                                expOSets.exp=expCont.exp
                                expOSets.cOrder_id=key
                                expOSets.fvp="Default"
                                expOSets.pCriteria=pCObj
                                expOSets.position=0
                                expOSets.sh_hd=0
                                expOSets.save()
                            except (PhoneCriteria.DoesNotExist):
                                pass
                                    


                
                              
                data={
                'success':'success',
                'exp_id':existExpId,
                'custom_exp_id':expCont.exp.custom_exp_id,
                'block_list':block_list
                }
                return JsonResponse(data)

class orderCriteria_Setup(TemplateView):
    def get(self,request):
        role_name=['']
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        flag="true"
        print(role)
        if  request.is_ajax():
            expCont = checkExpController(request)
            print("EXPCONTSS",expCont)
            if expCont:
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
                print("existCusId",existCusId)
            else:
                existCusId=""
                print("existCusId",existCusId)

            co_set_list=[]
            co_set_flag_length="one"
            co_set_show_dict={}
            co_set_hide_dict={}
            # try:
            #     exp_obj=Experiment.objects.get(custom_exp_id=existCusId)
            #     if (ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains="_Cdm.Def").exists()):
            #         co_obj_list=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains="_Cdm.Def")
            #         co_obj_list =co_obj_list.values_list("cOrder_id").distinct()
            #         co_obj_list = [item[0].split("_") for item in co_obj_list]
            #         co_obj_list = [item[0] for item in co_obj_list]
            #         co_set_list=co_obj_list
            #         print('co_obj_list',co_obj_list)
            #         if len(co_set_list)>1:
                        
            #             for co in co_set_list:
            #                 ECO_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains=co+"_Cdm.Def",sh_hd=1,pCriteria_id__status="default",pCriteria_id__priority="mendatory").order_by("id")
            #                 print("ECO_KNE",ECO_obj)
            #                 mandatory=list(ECO_obj.values_list("pCriteria_id__criteria_name",flat=True))
            #                 print("Man",mandatory)
            #                 # print("ExpCrtOrd",ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #                 ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains=co+"_Cdm.Def",sh_hd=0,pCriteria_id__status="default").order_by("id")
            #                 feature_to_hide=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #                 # list comprehension
            #                 feature_to_hide = [item[0] for item in feature_to_hide]
            #                 co_set_hide_dict[co]=feature_to_hide
            #                 print("hide",feature_to_hide)
            #                 ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains=co+"_Cdm.Def",sh_hd=1,pCriteria_id__status="default").order_by("id")
            #                 feature_to_display=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name","position"))
            #                 feature_to_display = [item[0] for item in feature_to_display]
            #                 co_set_show_dict[co]=feature_to_display
            #                 print("display",feature_to_display)
                            
            #                 co_set_flag_length="multiple"
            #                 print("co_set_show_dict",co_set_show_dict)
            #                 print("co_set_hide_dict",co_set_hide_dict)
            #                 flag="true"

            #         else:
            #             ECO_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains="_Cdm.Def",sh_hd=1,pCriteria_id__status="default",pCriteria_id__priority="mendatory").order_by("id")
            #             print("ECO_KNE",ECO_obj)
            #             mandatory=list(ECO_obj.values_list("pCriteria_id__criteria_name",flat=True))
            #             print("Man",mandatory)
            #             # print("ExpCrtOrd",ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #             ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains="_Cdm.Def",sh_hd=0,pCriteria_id__status="default").order_by("id")
            #             feature_to_hide=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #             print("hide",feature_to_hide)
            #             ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id__icontains="_Cdm.Def",sh_hd=1,pCriteria_id__status="default").order_by("id")
            #             feature_to_display=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name","position"))
            #             feature_to_display = [item[0] for item in feature_to_display]
            #             print("display",feature_to_display)
            #             flag="true"
            #     else:
            #         print("CO ELSE")
            #         feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('id')
            #         mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            #         feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('id')
            #         feature_to_display = list(feature_to_display.values_list("criteria_name","position"))
            #         feature_to_display = [item[0] for item in feature_to_display]

            #         print("feaeature_to_display",feature_to_display)
            #         print("feature_mand",mandatory)
                    
            #         feature_to_hide=list()
            #         flag="true"
            # except:
            print("CO EXCEPTION")
            feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('id')
            mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('id')
            feature_to_display = list(feature_to_display.values_list("criteria_name","position"))
            feature_to_display = [item[0] for item in feature_to_display]

            print("feaeature_to_disp",feature_to_display)
            print("feature_mand",mandatory)
                    
            feature_to_hide=list()
            flag="true"
          
            data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide,
                'mandatory':mandatory,
                'flag':flag,
                'co_set_show_dict':json.dumps(co_set_show_dict),
                "co_set_hide_dict":json.dumps(co_set_hide_dict),
                "co_set_flag_length":co_set_flag_length

            }
            return JsonResponse(data)

        
    def post(self,request):
         if request.is_ajax:
                crit_order_dict = request.POST.get('crit_order_dict')
                crit_order_dict=json.loads(crit_order_dict)
                crit_hide_dict = request.POST.get('crit_hide_dict')
                crit_hide_dict=json.loads(crit_hide_dict)
                featlevels_dic=request.POST.get('featlevels_dic')
                postedFLevels = json.loads(featlevels_dic)
                print("crit_order_dict",crit_order_dict)
                print("crit_hide_dict",crit_hide_dict)
                print("featlevels_dic",featlevels_dic)

                expCont = getExpController(request)
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
               
                # expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                # block_set = expCont.generateBlocks()
                # block_list = list(block_set.all().values('serial_no','levels_set'))
                # print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                # print(block_list)
                # save orderset Details in expCriteriaOrder
                if postedFLevels:
                    expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                    block_set = expCont.generateBlocks()
                    block_list = list(block_set.all().values('serial_no','levels_set'))
                    print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                else:
                    block_list=""
                print("block_list",block_list)

                #  1st check to see if postedDefFLevels exsists. 
                # if it does then 
                if postedDefFLevels:
                # call expCont.setDefFSet(newDefFLevels=postedDefFLevels,prompt=False)
                    expCont.setDefFSet(newDefFLevels=postedDefFLevels,prompt=False)
                
                exp_obj=Experiment.objects.get(custom_exp_id=existCusId)
                
                p_levList=list()
                if (ExpCriteriaOrder.objects.filter(exp=exp_obj).exists()):
                    ECO_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj)
                    ECO_obj.delete()
                else:
                    pass
                for key,s in crit_order_dict.items():
                    print(key,":",s)
                    p_levList.append(str(key))
                    for count, i in enumerate(s):
                        print("count",count)
                        print("ii",i)
                        try:
                            pCObj=PhoneCriteria.objects.get(criteria_name=i)
                            expOSets=ExpCriteriaOrder()
                            expOSets.exp=expCont.exp
                            expOSets.cOrder_id=str(key)
                            expOSets.pCriteria=pCObj
                            expOSets.fvp=str(key)
                            expOSets.position=count+1
                            expOSets.sh_hd=1
                            expOSets.save()
                        except (PhoneCriteria.DoesNotExist):
                            pass

                for key,s in crit_hide_dict.items():
                        print(key,":",s)
                        p_levList.append(str(key))
                        for count, i in enumerate(s):
                            print("count",count)
                            print("ii",i)
                            try:
                                pCObj=PhoneCriteria.objects.get(criteria_name=i)
                                expOSets=ExpCriteriaOrder()
                                expOSets.exp=expCont.exp
                                expOSets.cOrder_id=str(key)
                                expOSets.fvp=str(key)
                                expOSets.pCriteria=pCObj
                                expOSets.position=0
                                expOSets.sh_hd=0
                                expOSets.save()
                            except (PhoneCriteria.DoesNotExist):
                                pass

                            
                data={
                'success':'success',
                'exp_id':existExpId,
                'custom_exp_id':expCont.exp.custom_exp_id,
                'block_list':block_list
                }
                return JsonResponse(data)

class Cdm_On_Co_On_CriteriaSetup(TemplateView):
    def get(self,request):
        role_name=['']
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        flag="true"
        print(role)
        if  request.is_ajax():
            expCont = checkExpController(request)
            print("EXPCONTSS",expCont)
            if expCont:
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
                print("existCusId",existCusId)
            else:
                existCusId=""
                print("existCusId",existCusId)

            feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('id')
            mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('id')
            feature_to_display = list(feature_to_display.values_list("criteria_name","position"))
            feature_to_display = [item[0] for item in feature_to_display]

            print("feaeature_to_disp",feature_to_display)
            print("feature_mand",mandatory)
                    
            feature_to_hide=list()
            flag="true"
          
            data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide,
                'mandatory':mandatory,
                'flag':flag
            }
            return JsonResponse(data)
    def post(self,request):
          if request.is_ajax:
                crit_order_dict = request.POST.get('crit_order_dict')
                crit_order_dict=json.loads(crit_order_dict)
                crit_hide_dict = request.POST.get('crit_hide_dict')
                crit_hide_dict=json.loads(crit_hide_dict)
                featlevels_dic=request.POST.get('featlevels_dic')
                postedFLevels = json.loads(featlevels_dic)
                cataloglist=request.POST.get('cataloglist')
                cataloglist = json.loads(cataloglist)
                criteria_catalog_disp.objects.filter(id=1).update(catalog_crit_display_order=cataloglist)

                print("crit_order_dict",crit_order_dict)
                print("crit_hide_dict",crit_hide_dict)
                print("featlevels_dic",featlevels_dic)

                expCont = getExpController(request)
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
                expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                block_set = expCont.generateBlocks()
                block_list = list(block_set.all().values('serial_no','levels_set'))
                print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                print(block_list)
                # save orderset Details in expCriteriaOrder
                exp_obj=Experiment.objects.get(custom_exp_id=existCusId)
                
                p_levList=list()
                if (ExpCriteriaOrder.objects.filter(exp=exp_obj).exists()):
                    ECO_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj)
                    ECO_obj.delete()
                else:
                    pass
                for key,s in crit_order_dict.items():
                    print(key,":",s)
                    p_levList.append(str(key))
                    for count, i in enumerate(s):
                        # print("count",count)
                        # print("ii",i)
                        try:
                            pCObj=PhoneCriteria.objects.get(criteria_name=i)
                            expOSets=ExpCriteriaOrder()
                            expOSets.exp=expCont.exp
                            expOSets.cOrder_id=str(key)
                            expOSets.pCriteria=pCObj
                            expOSets.fvp=str(key)
                            expOSets.position=count+1
                            expOSets.sh_hd=1
                            expOSets.save()
                        except (PhoneCriteria.DoesNotExist):
                            pass

                for key,s in crit_hide_dict.items():
                        print(key,":",s)
                        p_levList.append(str(key))
                        for count, i in enumerate(s):
                            # print("count",count)
                            # print("ii",i)
                            try:
                                pCObj=PhoneCriteria.objects.get(criteria_name=i)
                                expOSets=ExpCriteriaOrder()
                                expOSets.exp=expCont.exp
                                expOSets.cOrder_id=str(key)
                                expOSets.fvp=str(key)
                                expOSets.pCriteria=pCObj
                                expOSets.position=0
                                expOSets.sh_hd=0
                                expOSets.save()
                            except (PhoneCriteria.DoesNotExist):
                                pass

                            
                data={
                'success':'success',
                'exp_id':existExpId,
                'custom_exp_id':expCont.exp.custom_exp_id,
                'block_list':block_list
                }
                return JsonResponse(data)

class cdmCriteria_Setup(TemplateView):
    def get(self,request):
        flag="true"
        role_name=['']
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        if  request.is_ajax():
           
            # A new check exp controller is made to only see if the exp 
            # exsists or not. if it exsists return its data other wise 
            # return none .
            expCont = checkExpController(request)
            print("EXPCONTSS",expCont)
            if expCont:
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
            else:
                existCusId=""
            print("existCusId",existCusId)
            # try:
            #     exp_obj=Experiment.objects.get(custom_exp_id=existCusId)            
            #     print("exp_obj",exp_obj)
            #     if (ExpCriteriaOrder.objects.filter(exp=exp_obj,fvp__contains="Cdm.Active").exists()):
            #         print("CDM Active")

            #         ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,fvp__contains="Cdm.Active",pCriteria_id__status="default",pCriteria_id__priority="mendatory").order_by("id")
            #         mandatory=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #         print("Man",mandatory)
            #         # print("ExpCrtOrd",ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #         ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=0,fvp__contains="Cdm.Active",pCriteria_id__status="default").order_by("id")
            #         feature_to_hide=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name",flat=True))
            #         # feature_to_hide = [item[0] for item in feature_to_hide]
            #         print("hide",feature_to_hide)
            #         ExpCrtOrd=ExpCriteriaOrder.objects.filter(exp=exp_obj,sh_hd=1,fvp__contains="Cdm.Active",pCriteria_id__status="default").order_by("id")
            #         feature_to_display=list(ExpCrtOrd.values_list("pCriteria_id__criteria_name","position"))
            #         feature_to_display = [item[0] for item in feature_to_display]
            #         print("display",feature_to_display)
            #         flag="true"
            #     else:
            #         print("CDM Else")

            #         feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('id')
            #         mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            #         feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('id')
            #         # feature_to_display = list(feature_to_display.values())
            #         feature_to_display =  list(feature_to_display.values_list("criteria_name","position"))
            #         feature_to_display = [item[0] for item in feature_to_display]
            #         print("feature_to_display--",feature_to_display)
            #         print("feature_mand",mandatory)
            #         feature_to_hide=list()
            #         flag="true"
            # except:
            print("CDM Exception")
            feature_mand=PhoneCriteria.objects.filter(status="default",priority="mendatory").order_by('id')
            mandatory=list(feature_mand.values_list("criteria_name",flat=True))
            feature_to_display=PhoneCriteria.objects.filter(status="default").order_by('id')
            # feature_to_display = list(feature_to_display.values())
            feature_to_display =  list(feature_to_display.values_list("criteria_name","position"))
            feature_to_display = [item[0] for item in feature_to_display]
            feature_to_hide=list()
            flag="true"

                
                
                

           
        
           
            print("feature",feature_to_display)
            print("feature_to hide",feature_to_hide)
            print("mandatory",mandatory)
            data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide,
                'mandatory':mandatory,
                'flag':flag
            }
            return JsonResponse(data)
    def post(self,request): 
           if request.is_ajax:
                cdm_crit_show_dict = request.POST.get('cdm_crit_show_dict')
                cdm_crit_show_dict= json.loads(cdm_crit_show_dict)
                cdm_crit_hide_dict = request.POST.get('cdm_crit_hide_dict')
                cdm_crit_hide_dict= json.loads(cdm_crit_hide_dict)
                featlevels_dic=request.POST.get('featlevels_dic')
                postedFLevels = json.loads(featlevels_dic)
                cataloglist=request.POST.get('cataloglist')
                cataloglist = json.loads(cataloglist)
                criteria_catalog_disp.objects.filter(id=1).update(catalog_crit_display_order=cataloglist)
                final_def_blocks_to_send = request.POST.get('final_def_blocks_to_send')
                postedDefFLevels=json.loads(final_def_blocks_to_send)
                print("final_def_blocks_to_send",final_def_blocks_to_send)
                
                print("cdm_crit_show_dict",cdm_crit_show_dict)
                print("cdm_crit_hide_dict",cdm_crit_hide_dict)
                
                expCont = getExpController(request)
                existExpId = expCont.exp.id
                existCusId=expCont.exp.custom_exp_id
                
                # expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                # block_set = expCont.generateBlocks()
                # block_list = list(block_set.all().values('serial_no','levels_set'))
                # print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                # print(block_list)
                # save orderset Details in expCriteriaOrder
                # Check to see if the exp obj already exists in the table. if it does then we need to update position and show_hide prop of  the rows containing the exp id. 
                # 1. based on the exp obj check if exp exists. if it does then 
                # 2. With the help of dict see the criteria_name, and fetch that row and update it the new position, sh_hd
                if postedFLevels:
                    expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                    block_set = expCont.generateBlocks()
                    block_list = list(block_set.all().values('serial_no','levels_set'))
                    print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                else:
                    block_list=""
                print("block_list",block_list)

                #  1st check to see if postedDefFLevels exsists. 
                # if it does then 
                if postedDefFLevels:
                # call expCont.setDefFSet(newDefFLevels=postedDefFLevels,prompt=False)
                    expCont.setDefFSet(newDefFLevels=postedDefFLevels,prompt=False)
                    
                print("---------------88888888888888888888888888---------------")

                exp_obj=Experiment.objects.get(custom_exp_id=existCusId)
                if (ExpCriteriaOrder.objects.filter(exp=exp_obj).exists()):
                    ECO_obj=ExpCriteriaOrder.objects.filter(exp=exp_obj)
                    ECO_obj.delete()
                else:
                    pass
                p_levList=list()
                for key,s in cdm_crit_show_dict.items():
                        print(key,":",s)
                        for count, i in enumerate(s):
                            print("count",count)
                            print("ii",i)
                            
                            try:
                                pCObj=PhoneCriteria.objects.get(criteria_name=i)
                                expOSets=ExpCriteriaOrder()
                                expOSets.exp=expCont.exp
                                expOSets.cOrder_id=key
                                expOSets.pCriteria=pCObj
                                expOSets.fvp="Cdm.Active_"+str(key)
                                expOSets.position=count+1
                                expOSets.sh_hd=1
                                expOSets.save()
                            except (PhoneCriteria.DoesNotExist):
                                pass
                for key,s in cdm_crit_hide_dict.items():
                        print(key,":",s)
                        for count, i in enumerate(s):
                            try:
                                pCObj=PhoneCriteria.objects.get(criteria_name=i)
                                expOSets=ExpCriteriaOrder()
                                expOSets.exp=expCont.exp
                                expOSets.cOrder_id=key
                                expOSets.fvp="Cdm.Active_"+str(key)
                                expOSets.pCriteria=pCObj
                                expOSets.position=0
                                expOSets.sh_hd=0
                                expOSets.save()
                            except (PhoneCriteria.DoesNotExist):
                                pass


                              
                data={
                'success':'success',
                'exp_id':existExpId,
                'custom_exp_id':expCont.exp.custom_exp_id,
                'block_list':block_list
                }
                return JsonResponse(data)      
@method_decorator(login_required, name='dispatch')
       
class adminSetup(TemplateView):
    # global  role
    global feature_to_display
    global feature_to_hide
    def get(self,request):
        global feature_to_display
        global feature_to_hide
        role_name=['']
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        print(role)
       
        if  request.is_ajax():
            feature_to_display = list(feature_to_display.values())
            print("feature to display",feature_to_display)
            numofsets=['CO.1','CO.2','CO.3']
            feature_to_hide = list(feature_to_hide.values())
            print("feature to hide",feature_to_hide)
            data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide,
                'numofsets':numofsets
            }
            return JsonResponse(data)
        else:
            if role=='Super_Admin':        
                feature_to_display=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role_id).order_by('position')
                numofsets=['CO.1','CO.2','CO.3']
                print("feature",feature_to_display)
                feature_to_hide=sort_feature.objects.filter(Q(sh_hd = 0),roles=role_id).order_by('position')    
                print("feature2",feature_to_hide)

            elif role=='Experiment_Admin':
                feature_to_display=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
                feature_to_hide=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')    
                # roleobj=Role.objects.get(pk=role)
                # role_name=roleobj.role_name
                # print(role_name)
                
            elif role=='Platform_Admin':
                feature_to_display=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
                feature_to_hide=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')    
                roleobj=Role.objects.get(pk=role)
                role_name=roleobj.role_name
                print(role_name)
            return render(request, 'webapp/admin_setup.html',{'numofsets':numofsets,'feature_to_display':feature_to_display,'feature_to_hide':feature_to_hide})

            
    def post(self,request):
        if request.is_ajax():
            print(request.user.id)
            userobj=User.objects.get(pk=request.user.id)
            print("user object",userobj.role_id_id)
            role_id=userobj.role_id_id
            roleobj=Role.objects.get(pk=role_id)
            role=roleobj.role_name
            print(role)
            numofsets=request.POST.get("numofsets")
            # get all feature/criteria 
            feature_to_disp=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role_id,exp_sets="Set1").order_by('position')
            feature_to_hide=sort_feature.objects.filter(Q(sh_hd = 0),roles=role_id,exp_sets="Set1").order_by('position')    

            data={
                    "numofsets":numofsets,
                    'feature_to_display':feature_to_disp,
                    'feature_to_hide':feature_to_hide
                    }
            return render(request,"webapp/admin_setup.html",data)

        
        

    #*****************************************************

    # if role==1:
    #    role_name=['Student']
    # elif role==2:
    #     role_name=['Professor']
    
    '''
    if request.user.is_authenticated:
                
        if request.user.is_student:
           global  role
           role=1
           feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
           ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
           colors=['black','white','gold']
           size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
        elif request.user.is_prof:
           role=2
           feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
           ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
           colors=['black','white','gold']
           size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
           #return redirect('/admin')
        else:
            print("in mobile redirect")
            return redirect('/mobileanl/mobile')  
           
    else:
        print("in else authenticate failed")
        return redirect('/mobileanl/mobile')  


    return render(request, 'webapp/admin_setup.html',{'feat':feat,'colors':colors,'size':size,'ft':ft})
    '''

# Create your views here.
def signUp(request):
     #m = request.session['username']
     #print(m)
     num_visits=request.session.get('num_visits', 0)
     request.session['num_visits'] = num_visits+1
     if request.method=="POST":
        print("in post")
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user.is_active:
                print("active")
                auth_login(request, user)
                if user.is_staff:
                    return redirect("admin")
                else:
                    return redirect("mobile/")  
     else:
        print("in sign else")
        form = UserCreationForm()
     return render(request,'webapp/signup.html',{'num_visits':num_visits,'form':form})
@method_decorator(login_required, name='dispatch')

class showFilter(TemplateView):
    def get(self,request):
        print("in filter")    
        print("global",role)
        # mobiles=samsung_phone.objects.all()
      
        feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')

        Colors=['black','white','gold']
        OS=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
        'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
        Size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
        Cpu=['octa-core','quad-core']
        back_camera=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
        battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
        data={ 
            'mobiles':mobiles,
            'Colors':Colors,
            'os':OS,
            'size':Size,
            'feat':feat,
            'cpu':Cpu,
            'back_cm':back_camera,
            'battery':battery
        }
        data={}
        return render(request,'webapp/showfilter.html',data)
filter_features=[]
class filter(TemplateView):
   
    def get(self,request):
        global filter_features
        if request.is_ajax():
            print("IN AJAX REQUEST")
            all_data_dict={}
            criterias_in_integer=['price',"Size","Weight"]
            # price=['100000','120000']
            # Size=['5','5.5','5.3','6.5','7']
            # Colors=['black','white','gold']
            # OS=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
            # 'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
            # # size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
            # Cpu=['octa-core','quad-core']
            # backcam=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
            # battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
            # Brand=['samsung','I Phone']
            # Chip=['Exynos 9810 Octa','Exynos 8895 Octa','Qualcomm Snapdragon 805','Exynos8890Octa','Quad-core (2 x 2.15 GHz Kryo + 2 x 1.6 GHz Kryo)','Exynos 7885 Octa','QualcommMSM8996Snapdragon820','Exynos7420','Exynos 7420 Octa','Exynos 7880 Octa','QualcommMSM8953Snapdragon625','Mediatek MT6757 Helio P20','Exynos 7870 SoC','Exynos 7870','1.4 GHz Quad-Core Cortex-A53','QualcommMSM816Snapdragon410','QualcommMSM8917Snapdragon425','1.2 GHz Quad-core Cortex-A53','Spreadtrum SC9830','MediatekMT6737T','Exynos3475','Spreadtrum SC9830','Spreadtrum','','']
            # resolution=['720 x 1280','540 x 960','480 x 800','1440 x 2960','1080 x 2220','1080 x 1920']      
            # weight=['163','195','173','174','155','191','157','172','132','0','181','169','179','135','160','170','143','159','146','156','138','131','122','126','153']  
            # dimensions=['147.6 x 68.7 x 8.4 mm','162.5 x 74.6 x 8.5 mm','159.5 x 73.4 x 8.1 mm','151.3 x 82.4 x 8.3 mm','148.9 x 68.1 x 8 mm','159.9 x 75.7 x 8.3 mm','150.9 x 72.6 x 7.7 mm','149.2 x 70.6 x 8.4 mm','143.4 x 70.8 x 6.9 mm','142.1 x 70.1 x 7 mm','153.2 x 76.1 x 7.6 mm','156.8 x 77.6 x 7.9 mm','146.1 x 71.4 x 7.9 mm','152.4 x 74.7 x 7.9 mm','146.8 x 75.3 x 8.9 mm','146.8 x 75.3 x 8.9 mm','156.7 x 78.8 x 8.1 mm','135.4 x 66.2 x 7.9 mm']
            # all_data_dic['price']=price
            # all_data_dic['Size']=Size
            # all_data_dic['Colors']=Colors
            # all_data_dic['OS']=OS
            # all_data_dic['Cpu']=Cpu
            # all_data_dic['backcam']=backcam
            # all_data_dic['battery']=battery
            # all_data_dic['Brand']=battery
            # all_data_dic['Ram']=["1GB","2GB","3GB","4GB"]
            # all_data_dic['Memory']=["1GB","2GB","3GB","4GB"]
            print(filter_features)
            gcritdt_obj=generalCriteriaData.objects.filter(criteria__in=filter_features)
            gcritdt_obj_list=list(gcritdt_obj.values_list("criteria__criteria_name","valuelist",'inputtype'))
            # criteria_name=gcritdt_obj_list[0][0]
            # value_list=gcritdt_obj_list[0][1]
            # value_list = [ float(x) for x in value_list ]
            # inputtype=gcritdt_obj_list[0][2]
            # all_data_dict[criteria_name]=[]
            # all_data_dict[criteria_name].append(value_list)
            # all_data_dict[criteria_name].append(inputtype)
            # min=value_list[0]
            # max=value_list[-1]
            # templist=[]
            # templist.append(min)
            # templist.append(max)
            # all_data_dict[criteria_name].append(templist)


            # print("criteria_name",criteria_name)
            # print("value_list",value_list)
            # print("inputtype",inputtype)
            for obj in gcritdt_obj_list:
                criteria_name=obj[0]
                value_list=obj[1]

                if criteria_name in criterias_in_integer:
                    value_list = [ float(x) for x in value_list ]

                inputtype=obj[2]
                if inputtype=="slider":
                    # get min and max of valuelist. and store in a list. 
                    min=value_list[0]
                    max=value_list[-1]
                    templist=[]
                    templist.append(min)
                    templist.append(max)
                    all_data_dict[criteria_name]=[]
                    all_data_dict[criteria_name].append(value_list)
                    all_data_dict[criteria_name].append(inputtype)
                    all_data_dict[criteria_name].append(templist)
                else:
                    all_data_dict[criteria_name]=[]
                    all_data_dict[criteria_name].append(value_list)
                    all_data_dict[criteria_name].append(inputtype)
            print(all_data_dict)



            data={
                "all_data_dict":all_data_dict,
                # 'feat':filter_features,
                # 'data_filter_feature':data_filter_feature
                }
            return JsonResponse(data)
        else:
            print(request.user.id)
            userobj=User.objects.get(pk=request.user.id)
            print("user object",userobj.role_id_id)
            role=userobj.role_id_id
            roleobj=Role.objects.get(pk=role)
            role=roleobj.role_name
            print(role)
            
            if role=='Super_Admin':
                pass
                # roles=1
                # filter_features=sort_feature.objects.filter(~Q(sh_hd = 0),roles=roles).order_by('position')
                # ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=roles).order_by('position')
                # print("In super admin",filter_features)
            elif role=='Subject':
                exp_obj=Experiment.objects.get(id=134)

                ExpCritObj=ExpCriteriaOrder.objects.filter(exp=exp_obj,cOrder_id="c.pruned",sh_hd=1)
                pcriteria_list=list(ExpCritObj.values_list("pCriteria",flat=True))
                filter_features=pcriteria_list
                
                # global role
                # roles=2
                # filter_features=sort_feature.objects.filter(~Q(sh_hd = 0),roles=roles).order_by('position')
                # ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=roles).order_by('position')
            # else:
            #     print("in mobile redirect")
            #     return redirect('/mobileanl/mobile')
            return render(request,'webapp/showfilter.html')
    
    def post(self,request):
        # print("ssss",(request.POST['first_choice_value']))
        # print("ssss",form.cleaned_data['first_choice_value'])
        global sizeofmob
        global filt_mobiles
        
        
        # if request.method=="POST":
            # first_choice = request.POST['first_choice_value']
            # print("fc",first_choice)
            # first_choice2 = request.POST['first_choice2_value']
            # print("fc2",first_choice2)
            # second_choice=request.POST['second_choice_value']
            # print("sc",second_choice)
            # third_choice=request.POST['third_choice_value']
            # print("tc",third_choice)
            # fourth_choice=request.POST['fourth_choice_value']
            # print("fc",fourth_choice)
            # fourth_choice2=request.POST['fourth_choice2_value']
            # print("f2c",fourth_choice2)
            # fifth_choice=request.POST['fifth_choice_value']
            # print("fc",fifth_choice)
            # six_choice=request.POST['six_choice_value']
            # print("sixc",six_choice)
            # seven_choice=request.POST['seven_choice_value']
            # print("sevc",seven_choice)
            # eight_choice=request.POST['eight_choice_value']
        
            # nine_choice=request.POST['nine_choice_value']
            
            # ten_choice=request.POST['ten_choice_value']
            
            # eleven_choice=request.POST['eleven_choice_value']
            # print("ele",eleven_choice)
            # twelve_choice=request.POST['twelve_choice_value']
        # filter_d={}
        if request.is_ajax():
            count=0
            element_data_dict = request.POST.get('element_data_dict')
            #print('d',d)
            element_data_dict = json.loads(element_data_dict)
            # print("filt_opt_sel",filt_opt_sel)
            filter_d=element_data_dict
            # return render(request,'webapp/mobile.html')  
            


        # filter_d = {  'Colors' : second_choice,
        #             'OS' : third_choice,
        #             'Size': {'1':fourth_choice,'2':fourth_choice2},
        #             'price':{'1':first_choice,'2':first_choice2},
        #             'Cpu'  : fifth_choice,
        #             'back_camera':six_choice,
        #             'battery' : seven_choice,
        #             'Mobile_Companny':eight_choice,
        #             'Chip':nine_choice,
        #             'Resolution':ten_choice,
        #             'Weight':eleven_choice,
        #             'Dimensions':twelve_choice
        #      }
        # print(filter_d)
            query_array = []
            temparray=[]
            
            argument_list = []    
            q_objects = Q()
    
            for key in filter_d:

                print("key",key)
                value=filter_d[key]
                print("value",value)
                if (filter_d[key] != ''):
                    if(type(value) == list ):
                        temparray=[]
                        for k in value:
                            if(k!=''):
                                # print("in size",k)
                                temparray.append(k)
                            # print("filter_d[key][k]",value[k])
                            # if (filter_d[key][k]!=''):
                            #     print("in size",filter_d[key][k])
                            #     temparray.append(filter_d[key][k])
                        print(temparray)
                        if  temparray:
                           
                            # query_array.append(' '+key +' BETWEEN '+temparray[0]+ ' AND '+ temparray[1] +" " )
                            
                            argument_list.append( Q(**{key+'__range':(temparray[0],temparray[1])}))
                            # kwargs={'{0}'__'{1}'.format(key,'range'):(temparray[0],temparray[1])}
                            # count=count+1
                    # elif(key == 'price'):
                    #     temparray=[]
                    #     for k in filter_d[key]:
                    #         if (filter_d[key][k]!=''):
                    #             print("in price",filter_d[key][k])
                    #             temparray.append(filter_d[key][k])
                    #     print(temparray)
                    #     if  temparray:
                    #         query_array.append(' '+key +' BETWEEN '+temparray[0]+ ' AND '+ temparray[1]+ " ")
                    else:
                       
                        var=filter_d[key]
                        # query_array.append(' '+key +' LIKE '+"'"+'%%'+var+'%%'+"'")
                        argument_list.append(Q(**{key+'__contains':var} ))
                    
                    
                
            # if len(query_array) != 0:
            if len(argument_list) !=0:

                # query = 'SELECT * FROM webapp_samsung_phone WHERE '+ 'AND ' .join(query_array)
                # query = 'SELECT * FROM webapp_mobilephones WHERE '+ 'AND ' .join(query_array)
                
                #old_query= '''SELECT * FROM webapp_samsung_phone where OS like'+"'"+'android v7.1.1 (nougat)'+"'''
                # print(query)
                # mobiles=samsung_phone.objects.raw(query)
                # filt_mobiles=mobilephones.objects.raw(query)
                
                filt_mobiles=mobilephones.objects.filter(reduce(operator.and_, argument_list)).order_by('id')
                sizeofmob=len(list(filt_mobiles))
                print(sizeofmob)
                
            else:
                # query = 'SELECT * FROM webapp_samsung_phone '
                # query = 'SELECT * FROM webapp_mobilephones '
                query=mobilephones.objects.all().order_by('id')
                # mobiles=samsung_phone.objects.raw(query)
                filt_mobiles=query
                
                sizeofmob=len(list(filt_mobiles))
                print(sizeofmob)
            print(filt_mobiles)
        
            filt_mobiles=filt_mobiles
            print("sizeofmob",sizeofmob)
            data={
                'filt_mobiles':"filt_mobiles",
                }

            return JsonResponse(data)

            
          
            
        # return render(request,'webapp/mobile.html',{'mobiles':mobiles})
        # return redirect('/mobile')

@method_decorator(login_required, name='dispatch')

class blogview (TemplateView):
    template_name='webapp/blog.html'
    
    def get(self,request):
        if request.user.has_perm('webapp.add_signup_table'):
            return redirect('/admin')
        else:
            return redirect('/mobileanl/admin_setup')
        '''
        print("in fucn",request.GET)
        if  request.user.is_staff:
            print("blog view",request.user.get_username)
            return redirect('/admin')
        else:
            return redirect('/mobileanl/mobile')
        return render(request,self.template_name)
        '''
    def post(self,request):
       
        '''
        if request.method=="POST":
            form=blogForm(request.POST)
            if form.is_valid():
                print("in blog request post")
                blog_item=form.save(commit=False)
                blog_item.save()
        else:
            print("in blog else")
            form=blogForm()
        return render(request,'webapp/blog.html',{'form':form})
        '''


def filteredMobileView(request):
    print("IN FILTERED MOBILE VIEW-->")
    template_name='webapp/mobile.html'
    if request.method=="GET":
       
        userobj=User.objects.get(pk=request.user.id)
        role=userobj.role_id_id

        roleobj=Role.objects.get(pk=role)
        role=roleobj.role_name
        global filt_mobiles
        
        if role=='Super_Admin':
            if filt_mobiles==None:
                filt_mobiles= mobilephones.objects.all() 
                print("mobiles ---<>",filt_mobiles)
                paginator = Paginator(filt_mobiles,2)
                page = request.GET.get('page')
                ex_mobile = paginator.get_page(page)
            else:
                print("filt_mobiles",filt_mobiles)
                print("in pass")
                paginator = Paginator(filt_mobiles,9)
                page = request.GET.get('page')
                ex_mobile = paginator.get_page(page)               
            template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
            
            
            return render(request,template_name,{'mobiles':ex_mobile ,'template_sidebar':template_sidebar})
        elif role=='Subject':
            if filt_mobiles==None:
                filt_mobiles= mobilephones.objects.all() 
                paginator = Paginator(filt_mobiles,9)
                page = request.GET.get('page')
                ex_mobile = paginator.get_page(page)
                template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
                return render(request,template_name,{'mobiles':ex_mobile,'template_sidebar':template_sidebar})
            else:
                print("mobiles",filt_mobiles)
                # uid = request.user.id
                # print(uid)
                # tuser = User.objects.get(username=uid)
                # exp_list = tuser.subject_set.values_list('exp', flat=True) 
                # exp_active = max(exp_list)    
                # mobilephones.objects.filter()            
                # phoneobjs=selectedAdminPhones.objects.filter(exp=134)
                # print(phoneobjs)
                # plist=[]
                # for pob in phoneobjs:
                #     print(pob)
                #     plist.append(pob.mob.id)
                # # print(plist)
                # print("SS",filt_mobiles[0].id)
                mobile_id_list=[]
                for mobile in filt_mobiles:
                    mobile_id_list.append(mobile.id)
                filt_mobiles=mobilephones.objects.filter(pk__in=mobile_id_list)
                paginator = Paginator(filt_mobiles,9)
                page = request.GET.get('page')
                ex_mobile = paginator.get_page(page)
                # using raw query paginator 'rawpaginator'
                # raw_qs = filt_mobiles
                # p = Paginator(raw_qs, 2)
                # page = request.GET.get('page')
                # filt_mobiles =p.page(1)
                

                template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
                return render(request,template_name,{'mobiles':ex_mobile,'template_sidebar':template_sidebar})
@method_decorator(login_required, name='dispatch')

class mobile_phone_view(TemplateView):
    template_name='webapp/mobile.html'
    def get(self,request):
        print("in phoneview")
        #form=mobile_phone_form(request.POST)
        querry_array=[]
        querry=''
        userobj=User.objects.get(pk=request.user.id)
        role=userobj.role_id_id
        roleobj=Role.objects.get(pk=role)
        role=roleobj.role_name
        global mobiles
        print("mobiles",mobiles)
        if role=='Super_Admin':
            
            mobiles= mobilephones.objects.all()
            print("mobiles ---<>",mobiles)
            paginator = Paginator(mobiles,9)
            print("paginator",paginator)
            page = request.GET.get('page')
            print("page",page)
            ex_mobiles = paginator.get_page(page)
            print("EX_MONILES",ex_mobiles)

            template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
            return render(request,self.template_name,{'mobiles':ex_mobiles,
            'template_sidebar':template_sidebar,
            'role':"Super_Admin",
            })
        elif role=='Subject':
            exp_list = userobj.subject_set.values_list('exp', flat=True) 
            # Getting the status codes that are active.
            exStatusCd_list=exStatusCd.objects.filter(status_code__gte=11)
            # Fetching that the experiments who has status code as active for the user/subject. 
            inner_qs = exp.objects.filter(id__in=list(exp_list),status_code__in=exStatusCd_list)
            # Using the experiment list for display
            print("inner_qs",list(inner_qs.values('id'))[0]['id'])
            explist=inner_qs.values('id')
            print("explst",explist)
            # Now we know how many experiments the subject is invovled. 
            # For now we'll hard code to get one subject having one active exp... 

            exp_obj=exp.objects.get(id=list(inner_qs.values('id'))[0]['id'])
            Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)

            # CHANGE THIS CODE... Changed...

            # exp_list = userobj.subject_set.values_list('exp', flat=True) 
            # inner_qs = exp.objects.filter(id__in=list(exp_list),status__contains="ACTIVE")
            # print("inner_qs",inner_qs)
            # exp_active = max(exp_list)  
            # print("ExpActive",exp_active)              
            phoneobjs=selectedAdminPhones.objects.filter(exp=exp_obj)
            print("pset_id",phoneobjs.values())
            print("ddd",list(phoneobjs.values_list('pset_id',flat=True)))
            pset_id=list(phoneobjs.values_list('pset_id',flat=True))
            global exp_feat_levels
            # if pset_id!=['P.All']:
            # if 'P.All' not in exp_feat_levels:
            #     print("pset id not P.All")
            #     print(phoneobjs)
            #     plist=[]
            #     for pob in phoneobjs:
            #         print(pob)
            #         plist.append(pob.mob.id)
            #     # print(plist)
            #     filt_mobiles=mobilephones.objects.filter(pk__in=plist)
            #     print("filt_mobiles",filt_mobiles)
            #     paginator = Paginator(filt_mobiles,9)
            #     page = request.GET.get('page')
            #     ex_mobiles = paginator.get_page(page)
            # else:
            #     print("pset id  P.All")

            #     mobiles= mobilephones.objects.all() 
            #     paginator = Paginator(mobiles,9)
            #     page = request.GET.get('page')
            #     ex_mobiles = paginator.get_page(page)
            ex_mobiles=[]   
            template_sidebar='webapp/sidebartemplates/sidebartemp_subject.html'
            return render(request,self.template_name,{'mobiles':ex_mobiles,'template_sidebar':template_sidebar})
           
        else:
            mobiles= mobilephones.objects.all() 
            paginator = Paginator(mobiles,9)
            page = request.GET.get('page')
            ex_mobiles = paginator.get_page(page)
            
            return render(request,self.template_name,{'mobiles':ex_mobiles})
    def post(self,request):
        if request.method=="POST":
            form=mobile_phone_form(request.POST)
            if form.is_valid():
                print("in blog request post")
                mob_item=form.save(commit=False)
                mob_item.save()
        else:
            print("in blog else")
            form=mobile_phone_form()
            return render(request,self.template_name,{'form':form})

    def one_mobile_func(request,id):
        id1=id
        print(id1)
        # singlemob=samsung_phone.objects.filter_d(id=id1)
        singlemob=mobilephones.objects.filter(id=id1)
        print(singlemob)
        return render(request,'webapp/one_mobile_info.html',{
            'singlemob':singlemob
            })
        

def ImportCsv_submit(request):
    if request.method == 'POST':
        form = NameForm(request.POST)
        if form.is_valid():
            #data=[]
            tablename=form.cleaned_data.get('tablename')
            csvfilepath=form.cleaned_data.get('csvfilepath')
            #print(type(csvfilepath))
            data.extend((tablename,csvfilepath))
            status=populate_Table(tablename,csvfilepath)
        
            return render (request, 'webapp/importcsv_form_display.html',
                {
                'status':filepath
                })
    else :
        form = NameForm()
        return render(request,'webapp/importcsv_submit.html',{'form': form})
#--------------------------------------------------------------------------------------------------
# Experiment admin related views.
@method_decorator(login_required, name='dispatch')

class  BiasTestFeature(TemplateView):
    template_name='webapp/biasfeaturetest.html'
    def get(self,request):  
        #epadmin_obj=Experiment_Admin(request.user.last_name,request.user.id)
        #experiment_admin_data=epadmin_obj.getExperiment_AdminInfo()

        #print(experiment_admin_data)
        #check permissions of the user...
        #if experiment_admin or superuser confirmed
            ## call all functions... 
        # if experiment_Staff 
           ## call view function
         #**************************************************
        # This code gets the user id, then on bases of role we will assign the templates.
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role=userobj.role_id_id
        roleobj=Role.objects.get(pk=role)
        role=roleobj.role_name
        print('role',role)
        if role=='Super_Admin':
            template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
            expadm_maincontent_temp='webapp/main_content_temps/biaswebfeature/main_cont_temp_expadmin.html'
        elif role=='Experimental_Admin':
            template_sidebar='webapp/sidebartemplates/sidebartemp_expadm.html'
            expadm_maincontent_temp='webapp/main_content_temps/biaswebfeature/main_cont_temp_expadmin.html'
        elif role=='Platform_Admin':
            template_sidebar='webapp/sidebartemplates/sidebartemp_pltfadm.html'
         #*****************************************************
        return render(request,self.template_name,{'template_sidebar':template_sidebar,
                                                    'role_name':role,
                                                    'expadm_maincontent_temp':expadm_maincontent_temp
                                                    })
    def post(self,request):
        return render(request,'webapp/biasfeaturetest.html')
@method_decorator(login_required, name='dispatch')

class ManageShortList(TemplateView):
    def get(self,request):
        # mobiles= samsung_phone.objects.all()
        mobiles= mobilephones.objects.all()
        paginator = Paginator(mobiles,9)
        page = request.GET.get('page')
        mobiles = paginator.get_page(page)
        print(mobiles)
        return render(request,'webapp/mangeshortlist.html',{'mobiles':mobiles})

    def post(self,request):
        if request.is_ajax:
        # print("ajax",request.POST.get('data'))
            ####print("PST",request.POST.get('d')) 
            d = request.POST.get('data[0]')
            d=json.loads(d)
            arrr = request.POST.get('data[1]')
            arr=json.dumps(arrr)
            print(arr)
            print(d)
        return render(request,'webapp/mangeshortlist.html',{'mobiles':mobiles})
def subDetails(request):
    if request.is_ajax:
            arrlist=[]
        # print("ajax",request.POST.get('data'))
            ####print("PST",request.POST.get('d')) 
            d = request.POST.get('d')
        ### print('JSONLOADS',eval(d))
            b = json.loads(d)
            print(b)
            pltfobj=platform_feature.objects.get(feature_symbol=b)
            arrlist=pltfobj.feature_levels
            print(type(arrlist))    
            print(arrlist)
    return HttpResponse(json.dumps(arrlist), content_type='application/json')
## Function for getting the sample file. 
def selfDefault(request):
    expCont = getExpController(request)
    if request.method == 'POST':
        if request.is_ajax:
            data = request.POST.get('csvfiledata')
            #print('d',d)
            json_data = json.loads(data)
            print("CHECKING FILE:\n",json_data)
            json_data=[i.replace('\r','') for i in json_data]  
            print('head',type(json_data[0]))
            filefields = json_data[0].split(",")
            #label=json_data[0]
            print('filefields',filefields)
            filebody=[i.split(',') for i in json_data[1:]] 
            print(type(filebody))
            print('file body')
            print(filebody)
            arr_filebody = np.array(filebody)
            print('arr_filebody')
            print(arr_filebody)
            dataframe= pd.DataFrame.from_records(arr_filebody,columns=filefields)
            print('dataframe')
            print(dataframe)
            expCont.subjData=dataframe
            expCont.idField='ROLLNO'
            batchesTitle = 'BATCHES'
            defaultNo=1
            # pickleExpController(expCont)
            # expCont=getExpController(request)
           
            
            expCont.subjData = expCont.assigner.splitInBins(defaultNo, batchesTitle)
            expCont.setBatchesTitle(batchesTitle)
            expCont.saveSubjects()
            pickleExpController(expCont)
            data=expCont.subjData.groupby(batchesTitle).size().to_dict()

    return JsonResponse(data)
def uploadSampleFile(request):
    expCont = getExpController(request)
    print('expContid',expCont.idField)
    
    if request.method == 'POST':
        if request.is_ajax:
            data = request.POST.get('csvfiledata')
            #print('d',d)
            json_data = json.loads(data)
            
            #print('json_data',type(json_data))
            json_data=[i.replace('\r','') for i in json_data]  
            ## check last index of the json data. 
            ## it'll tell which assign type it is. on the basis of assign type perform action. 
            print('FILE DATA')
            print(json_data)
            assign_type=json_data.pop()
            assign_type=assign_type.replace('\n','')
            print(assign_type)
            
            if assign_type=='self':
                customlabels=json_data.pop()
                customlabels=customlabels.replace('\n','')
                customlabels=customlabels.split(',')
                print('customlabel',customlabels)
                batch_num=json_data.pop()
                batch_num=batch_num.replace('\n','')
                print('batch number',batch_num)
                batch_num=int(batch_num)
                batch_name=json_data.pop()
                batch_name=batch_name.replace('\n','')
                print('batch_name',batch_name)
                batch_title_field=json_data.pop()
                batch_title_field=batch_title_field.replace('\n','')
                print('batch_title_field',batch_title_field)
                email_field=json_data.pop()
                email_field=email_field.replace('\n','')
                print(email_field)
                customid_field=json_data.pop()
                customid_field=customid_field.replace('\n','')
                print('customid_field',customid_field)
               


                print('head',type(json_data[0]))
                filefields = json_data[0].split(",")
                #label=json_data[0]
                print('filefields',filefields)
                filebody=[i.split(',') for i in json_data[1:]] 
                print(type(filebody))
                print('file body')
                print(filebody)
                arr_filebody = np.array(filebody)
                print('arr_filebody')
                print(arr_filebody)
                dataframe= pd.DataFrame.from_records(arr_filebody,columns=filefields)
                print('dataframe')
                #ORDER CORRECTION:
                #FIRST DECLARE ID FIELD - ELSE USER SAVING WILL BE INCORRECT
                if customid_field!='None':
                    expCont.setIdField(customid_field)
                    print('ExpCont.idField')
                    print(expCont.idField)
                if batch_title_field=='None':
                    expCont.setBatchesTitle(batch_name)
                    selfDefBatches = True
                #pickleExpController(expCont)
                #expCont=getExpController(request)
                print('>>>BEFORE subjdata head')
                # print('dataframe')
                print(dataframe.head())
                expCont.subjData=dataframe
                
                print('subdata head')
                print(expCont.subjData.head())
                expCont.subjData=expCont.assigner.splitInBins(
                    no_bins = batch_num,
                    binName = batch_name,
                    df = dataframe, #PREVIOUSLY MISSING LINE IN ASSIGNER LOGIC NO NEED TO PICKLE!
                    binLabels = customlabels
                )
                print('AFTER >>>> Newly BATCHED: ExpCont_SubjData')
                print(expCont.subjData.head())
                #expCont.fSet = None  #Needed before pickling
                pickleExpController(expCont)
                
                expCont.saveSubjects()
                dSubBatches=expCont.subjData

                print("controller df")
                # print(dSubBatches)
                print("contdf ",type(dSubBatches))
                dataframe=dSubBatches
                print('DATAFRAME')
                # print(dataframe)
                dict_all={}
                
                groupby_batch_name=dataframe.groupby(batch_name)
                groupby_batch_name_size=groupby_batch_name.size()
                # batchsize=dataframe.size()
                dataframe=dataframe.to_json()
                
                groupby_batch_name_size=groupby_batch_name_size.to_json()
                # groupsize=dSubBatches.size()
                # groupsize=groupsize.to_json()

                dict_all['1']=dataframe
                dict_all['batches']=groupby_batch_name_size
                dict_all['exp_id']= expCont.exp.id
                dict_all['custom_exp_id']=expCont.exp.custom_exp_id
                
                # dict_all['2']=groupsize
                print('dictionary all')
                
                print(dict_all)
                

                return HttpResponse(json.dumps(dict_all))#dSubBatches_grp_A_json)
               
                ## ONCE THE DATA IS PROCESSED WE CAN SAVE INTO EXCEL OR CSV FILE
                #print(dSubBatches.get_group('1'))
    else:
        pass
    return render(request, 'webapp/crudexperiment/create_experiment.html')    

def postExp(request):
        admin_id='ses-007'
        if request.is_ajax:
            data = request.POST.get('csvfiledata')
            #print('d',d)
            
            # object retrieving example
            expCont = pickle.load( open( "save.p", "rb" ) )
            print(expCont.exp.capacity)
            json_data = json.loads(data)
            json_data=[i.replace('\r','') for i in json_data]  
            batch_field_name=json_data.pop()
            email=json_data.pop()
            custom_id=json_data.pop()
            print(batch_field_name)
            print(custom_id)
            filefields = json_data[0].split(",")
            print('filefields',filefields)
            filebody=[i.split(',') for i in json_data[1:-1]] 
            print(type(filebody))
            print(filebody)
            arr_filebody = np.array(filebody)
            print(arr_filebody) 
            dataframe= pd.DataFrame.from_records(arr_filebody,columns=filefields)
            print("filedata")
            print(dataframe)
            if custom_id!='None':
                expCont.setIdField(custom_id)
            if batch_field_name!='None':
                expCont.setBatchesTitle(batch_field_name)
            expCont.saveSubjects(dataframe)
            #object storing 
            pickle.dump( expCont, open( "save.p", "wb" ) )
            print(expCont.exp.subject_set.all())
            print(expCont.subjData.groupby(batch_field_name).size())
        return HttpResponse()

def deleteAllSubjects(request):
    expCont=getExpController(request)
    expCont.deleteAllSubjects()
    
    pickleExpController(expCont)
    data = {}
    return JsonResponse(data)

def getExpController(request):
    try:
        cest_obj=customExpSessionTable.objects.aggregate(Max('expid'))
        print("ssss",cest_obj)
        print("qqqqqqqq",cest_obj['expid__max'])
        sess_expId=cest_obj['expid__max']
        # sess_expId = request.session['sess_expId']
        # print("session>>>>>>>>>>>>>>",request.session['sess_expId'])

        # print('SESSION ID',sess_expId)
    except KeyError:
        print("session_________")

        sess_expId = None
    if sess_expId:
        print("----->>>>>RETRIEVED EXP ID:",sess_expId,"FROM SESSION<<<<<<-----")
        print(request.user.custom_id,":",request.user.username)
        expAdminId = request.user.custom_id
        expCont = ExperimentController(a_id=expAdminId,e_id=sess_expId)
        
        print("Exp Custom Id:",expCont.exp.custom_exp_id)
        print("The following features are ALREADY enabled:")
        print(list(expCont.exp.experiment_feature_set.all()))
        try:
            print('in try pickle expCont')
            pickledExpCont = pickle.load( open("expCont4.p", "rb") )
            print('pickledExpCont.subjData')
            print(pickledExpCont.subjData)
        except:
            print('in except pickled ExpCont=None')
            pickledExpCont = None
        if pickledExpCont:
            print('in if condition if pickle exsists')
            expCont.subjData = pickledExpCont.subjData
            expCont.assigner.df = expCont.subjData
            print('IN GETEXP CONT expCont.assigner.df',expCont.assigner.df.head())
            expCont.idField = pickledExpCont.idField
            #POSSIBLY TRANSFER OTEHR THINGS AS WELL
            #CAN'T USE THE PICKLED EXP CONT DIRECTLY AS all funcitons are not transferred as expected
        else:
            print('in else cond to save obj in pickle')
            pickleExpController(expCont)
    else: #CREATE
        print('CREATING NEW EXPERIMENT  ')
        print("request.user.custom_id________",request.user.custom_id)
        expAdminId = request.user.custom_id
        print('expAdminId',expAdminId)
        expCont = ExperimentController(a_id=expAdminId)
        print('NEW Exp id',expCont.exp.id)
        # Default Session Maintenance
        cest_obj=customExpSessionTable()
        cest_obj.expid=expCont.exp.id
        cest_obj.cusexpid=expCont.exp.custom_exp_id
        cest_obj.save()
        # Default Session Maintenance
        # request.session['sess_expId'] = expCont.exp.id
        # request.session['sess_custExpId'] = expCont.exp.custom_exp_id
        print('request.session',request.session['sess_custExpId'] )
        print("SAVED NEW EXPERIMENT TO SESSION---->>>>>>")

    return expCont

def checkExpController(request):
    try:
        sess_expId = request.session['sess_expId']
        print('SESSION ID',sess_expId)
    except KeyError:
        sess_expId = None
    if sess_expId:
        expAdminId = request.user.custom_id
        expCont = ExperimentController(a_id=expAdminId,e_id=sess_expId)
    else: 
        expCont=None
    
    return expCont



def pickleExpController(expCont):
    pickle.dump(expCont, open('expCont4.p','wb'))

def getSavedSubjectDataExpCont(request):
    if request.method == 'POST':
        if request.is_ajax:
            pickleExpCont=pickle.load( open("expCont4.p", "rb") )
            subject_data=pickleExpCont.subjData
            subject_data=subject_data.to_dict()
            data={
                'subject_data':subject_data
            }
            return JsonResponse(data)

def importSubjects(request):
    expCont = getExpController(request)
    if request.is_ajax:
        data = request.POST.get('csvfiledata')
        json_data = json.loads(data)
        print('file data')
        print(json_data)
        json_data=[i.replace('\r','') for i in json_data]  
        print('file data')
        print(json_data)
        batch_field_name=json_data.pop()
        email=json_data.pop()
        custom_id=json_data.pop()
        print(batch_field_name)
        print(custom_id)
        filefields = json_data[0].split(",")
        print('filefields',filefields)
        filebody=[i.split(',') for i in json_data[1:]] 
        print(type(filebody))
        print(filebody)
        arr_filebody = np.array(filebody)
        print(arr_filebody) 
        dataframe= pd.DataFrame.from_records(arr_filebody,columns=filefields)
        print("filedata")
        print(dataframe)
        if custom_id!='None':
            expCont.setIdField(custom_id)
        if batch_field_name!='None':
            expCont.setBatchesTitle(batch_field_name)
            preDefBatches = True
        expCont.saveSubjects(dataframe)
        print(expCont.exp.subject_set.all())
        print('subjData:\n',expCont.subjData)
        pickleExpController(expCont) #pickle so that we can retrieve the subjData
        if preDefBatches:
            batchGpDict = expCont.subjData.groupby(batch_field_name).size().to_dict()
            print(batchGpDict)
        else:
            batchGpDict = ""
        data = {    'exp_id':expCont.exp.id,
                    'custom_exp_id':expCont.exp.custom_exp_id,
                    'batches':batchGpDict,
                    'batch_field':batch_field_name
                    }
        return JsonResponse(data)
    #return HttpResponse()
        
def assignToBlocks(request):
    #get the expCont
    expCont = getExpController(request)
    blocksBreakUp = "HELLO!"
    if request.is_ajax:
        print("Are there batches>>>",expCont.exp.batches_title)
        print("Data in Exp Cont\n", expCont.assigner.df)
        if not expCont.subjData.empty:
            print('if exp subjdata is not empty')
            blocksBreakUp = expCont.assignToBlocks()
            print('blocksBreakUp type',type(blocksBreakUp))
            #blocksBreakUp = blocksBreakUp.reset_index()
            print(blocksBreakUp)
            # print(blocksBreakUp[['SECTION ']])
            
            print(blocksBreakUp.index)
            #blocksBreakUp=blocksBreakUp[['A','B']]
            blocksBreakUp = blocksBreakUp.to_json(orient='index')#to_html(table_id="blocksBreakUp") #
            print("blocksBreakUp",blocksBreakUp)
        else:
            blocksBreakUp = "Empty"

        data = {    'exp_id':expCont.exp.id,
                    'custom_exp_id':expCont.exp.custom_exp_id,
                    'blocks':blocksBreakUp
        }
        #create to_json dictionary of blocks (by batches, ie. index-wise, then row-wise)
        return JsonResponse(data, safe=False)
def removeSessionObj(request):
    #Custom Session Maintenance 

    cest_obj=customExpSessionTable.objects.aggregate(Max('expid'))
    print("cest_obj",cest_obj)
    sess_expId=cest_obj['expid__max']
    obj=customExpSessionTable.objects.get(expid=sess_expId)
    obj.delete()

    # Default/Old session maintainance
    # try:
    #     filepath = Path("C:/biasweb/expCont4.p")
    # except FileNotFoundError:
    #     filepath=None
    # else:
    #     if filepath.exists():
    #         os.remove('C:/biasweb/expCont4.p')
    #     if request.session['sess_expId']:
    #         del request.session['sess_expId']
    #     return HttpResponse()


def importExcel(request):
    if request.method == 'POST':
        if request.is_ajax:
            data = request.POST.get('excel_data')
            #print('d',d)
            json_data = json.loads(data)
            print(json_data)

            print(type(json_data))
            #This module implements a file-like class, StringIO, that reads and writes a string buffer (also known as memory files).
            df = pd.read_csv(StringIO(json_data))
            print(df)
            data={
                'data':df
            }
            
    return HttpResponse()
def saveExperiment(request):
    if request.method == 'POST':
        if request.is_ajax:
            data = request.POST.get('ftDict_chkbxDict_blkLst')
            
            #print('d',d)
            json_data = json.loads(data)
            print(json_data['feat_dict'])
            print(json_data['checbox_id_dict'])
            print(json_data['blockList_temp'])
            data={
                'status':'success'
            }
    return JsonResponse(data)
@method_decorator(login_required, name='dispatch')
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

class createExperiment(TemplateView): 
    '''
    Class Defination/Functionality.
        1- It has four functions Get,Post,addDesp and getDefaultFLevelsFromPlatformFeature
        2- Get function has ajax and non ajax condition. 
            -- Non Ajax Cond- Saves or updates phone criteria in PhoneCriteria
            -- Ajax Cond- When the page is loaded and ajax(get) call is made which 
                          is recieved by it.
                        - It unloads the price range,brand name sent from html. 
                        - uses the price range and brand name to get all mobile phones and sends the data back to html. 
        3- Post Function has ajax condition. 
            -- Unloads feture level dict and default F Levels. 
            -- getExpController is called
            -- Then expCont.setFSet is run for Def and Admin Defined F lvls. 
        4- addDesp func will save desp about exp in exp ob. 
        5- getDefaultFLevelsFromPlatformFeature Not in use But will save default featLvls in expdefFlvls...   
    '''
    template_name='webapp/crudexperiment/create_experiment.html'
    
    def get(self,request):  
      
        platformfeatobj=platform_feature.objects.all()
        userobj=User.objects.get(pk=request.user.id)
        role=userobj.role_id_id
        roleobj=Role.objects.get(pk=role)
        role=roleobj.role_name
        
        # samsung_phones=''
        mobilephones_str=''
        if request.is_ajax():
           
                
            print('Ajax')
            print(platformfeatobj.values_list('feature_symbol',"feature_levels"))
            price_range_values = request.GET.get('price_range_values')
            brandnames = request.GET.get('brandnames')

            print(price_range_values)
           
            print("in if ")
            print('price_range_values',price_range_values)
            price_range_values = json.loads(price_range_values)
            if brandnames:
                brandnames = json.loads(brandnames)

            price_range=[]
            price_range.append(int(price_range_values[0]))
            price_range.append(int(price_range_values[1]))

            # mobiles_retrieved=samsung_phone.objects.filter(price_in_pkr__range=(price_range_values[0], price_range_values[1]))
            if not brandnames:
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range_values[0], price_range_values[1])).order_by('-id') 
              
            else:
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range_values[0], price_range_values[1]),Brand__in=brandnames).order_by('id') 
                

            # print(mobiles_retrieved) 
            mobiles_retrieved_list = list(mobiles_retrieved.values())
            mobilephones_str=mobiles_retrieved_list
            

            # print("mobilephones_str",mobilephones_str)
            print("price_range",price_range)
            return JsonResponse(
            {  
                 'mobilephones':mobilephones_str,
                "price_range_values":price_range
            }
            )
            
        else:
            print("NOT AJAX")
            # samsung_phones= samsung_phone.objects.all()
            phonecritlist=[]

            exclfields=['selectedadminphones','id','imagepath1','imagepath2','Whats_new',"Mobile_Name","price_in_usd"]
            # Get the mobile phone fields and then save the fields in phone criteria
            [phonecritlist.append(f.name) for f in mobilephones._meta.get_fields() if f.name not in exclfields]
            print(phonecritlist)
            for count,crit in enumerate(phonecritlist):
                if (PhoneCriteria.objects.filter(criteria_name=crit).exists()):
                    pcrt_obj=PhoneCriteria.objects.get(criteria_name=crit)
                    pcrt_obj.position=count
                    pcrt_obj.save()

                else: 
                    pcrt_obj=PhoneCriteria()
                    pcrt_obj.criteria_name=crit
                    pcrt_obj.status="default"
                    pcrt_obj.priority="mendatory"
                    pcrt_obj.position=count
                    pcrt_obj.save()

            m_p= mobilephones.objects.all() 
            # print("mobile_phones",m_p)
            # paginator = Paginator(m_p,9)
            # page = request.GET.get('page')
            # mobile_phones__str = paginator.get_page(page)

        
            if role=='Super_Admin':
                # samsung_phones= samsung_phone.objects.all() 
                # paginator = Paginator(samsung_phones,9)
                # page = request.GET.get('page')
                # samsung_phones = paginator.get_page(page)
                # print("samsung_phones",samsung_phones)
                # print("mobilephones",mobile_phones__str)
            
                creat_exp_template_sidebar='webapp/sidebartemplates/createExpSideBars/crtExpsidebartemp_exp.html'
                creat_exp_template_sidebar2='webapp/sidebartemplates/createExpSideBars/crtExpsidebartemp_exp2.html'

            elif role=='Experimental_Admin':
                # samsung_phones= samsung_phone.objects.all() 
                # paginator = Paginator(samsung_phones,9)
                # page = request.GET.get('page')
                # samsung_phones = paginator.get_page(page)
                # print(samsung_phones)
                # print(mobilephones)
                creat_exp_template_sidebar='webapp/sidebartemplates/createExpSideBars/crtExpsidebartemp_exp.html'
            elif role=='Platform_Admin':
                pass
            # Custom exp session maintenance
            try:
                cest_obj=customExpSessionTable.objects.aggregate(Max('expid'))
                print("cest_obj",cest_obj)
                sess_expId=cest_obj['expid__max']
                obj=customExpSessionTable.objects.get(expid=sess_expId)
                sess_custExpId=obj.cusexpid
            except:
                sess_expId = ""
                sess_custExpId = "123"



            # Defualt exp session maintenance
            # try:
            #     sess_expId = request.session['sess_expId']
            #     print("sesid",sess_expId)
            # except KeyError:
            #     sess_expId = ""
            # try:
            #     sess_custExpId = request.session['sess_custExpId']
            # except KeyError:
            #     sess_custExpId = "123"
            
            return render(request,self.template_name,
            {  'creat_exp_template_sidebar':creat_exp_template_sidebar,
               'creat_exp_template_sidebar2':creat_exp_template_sidebar2,
                'platformfeatobj':platformfeatobj,
                'sess_expId':sess_expId,
                'sess_custExpId':sess_custExpId,
                # 'samsung_phones':samsung_phones
            }
            )
                                        
                                    
    def post(self,request):
        if request.method=="POST":
            print("====IN CREATEEXP POST METHOD====")
            data = {'data':"data"}

            if request.is_ajax:
                d = request.POST.get('block_feat_dict')
                print(request.POST.get('price_range_values'))
                #print('d',d)
                postedFLevels = json.loads(d)
                print('postedFLevels',postedFLevels)
                # if postedFLevels is none then remove everything ..... 
                print('b',type(postedFLevels),postedFLevels)

                final_def_blocks_to_send = request.POST.get('final_def_blocks_to_send')
                final_def_blocks_to_send=json.loads(final_def_blocks_to_send)
                print("final_def_blocks_to_send",final_def_blocks_to_send)
                
                #CREATE EXPERIMENT CONTROLLER AND INITIALIZE
                #returns either a controller for new experiment
                #or for existing one [TODO: CHECK STATUS OF EXPERIMENT AS IN DESIGN_MODE]
                expCont = getExpController(request)
                existExpId = expCont.exp.id

                #SET FLEVELS
                #@Todo: TEST: Add Condition if postedFLevels are empty then newFLevels set to None)
                if not postedFLevels:
                    postedFLevels=None
                expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                if postedFLevels is not None:
                    block_set = expCont.generateBlocks()
                    block_list = list(block_set.all().values('serial_no','levels_set'))
                else:
                    block_list=[]

                    
                # # blockStr = "\n".join(str(b) for b in expCont.exp.block_set.all())
                print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                print(block_list)
                data = {
                    'exp_id':existExpId,
                    'custom_exp_id':expCont.exp.custom_exp_id,
                    'block_list':block_list
                }
                return JsonResponse(data) #, safe=False)
        #return render(request,'webapp/crudexperiment/create_experiment.html',data)

    def addDesp(request):
        # If experiment object exsists then add the descp returned from ajax request. 
        if request.is_ajax():
            exp_description= request.POST.get('exp_description')
            exp_id= request.POST.get('exp_id')

            print("exp_des")
            expCont = getExpController(request)
            existExpId = expCont.exp.id
            exp.objects.filter(id=existExpId).update(desc=exp_description)
            print(exp_description)

            return JsonResponse({'data':"success"})
    def getDefaultFLevelsFromPlatformFeature(request):
        platformfeatobj=platform_feature.objects.all()

        if request.is_ajax():
            global def_featlvl_frm_pf_dict
            def_platf_list=list(platformfeatobj.values_list('feature_symbol',"default_levels"))
            print(type(def_platf_list))
            
            for i in def_platf_list:
                def_featlvl_frm_pf_dict[i[0]]=i[1]
            data={
                'def_featlvl_frm_pf_dict':json.dumps(def_featlvl_frm_pf_dict),
            }
            return JsonResponse(data)


statusCode_list=[]
exp_wrt_statuscode={}
crit_exp_wrt_statuscode={}
@method_decorator(login_required, name='dispatch')

class ManageExperiment(TemplateView):
    '''
    It has two Functions  get and post.. 
    1- Get Function- 
    '''
    
    template_name='webapp/crudexperiment/manage_experiment.html'
    template_sidebar="webapp/sidebartemplates/sidebartemp_superadmin.html"
    
    
    def get(self,request):
        
        if request.is_ajax():
            userobj=User.objects.get(pk=request.user.id)
            role=userobj.role_id_id
            roleobj=Role.objects.get(pk=role)
            role=roleobj.role_name
            if role=='Super_Admin':
                global statusCode_list
                global exp_wrt_statuscode
                statusCode_list=exStatusCd.objects.values_list("status_code","status_name").distinct()
                statusCode_list=list(statusCode_list)
                print(statusCode_list)                    
                exStatusCd_index=exStatusCd.objects.get(status_code=11)

               

                for code in statusCode_list:
                    foo_dict={}
                    temp_dict={}
                    print(code[0])
                    print(code[1])
                    # code[0] contains the index and code[1] name of the status
                    exStatusCd_index=exStatusCd.objects.get(status_code=code[0])
                    all_exp_list_obj = exp.objects.filter(status_code=exStatusCd_index)
                    all_exp_list_values=list(all_exp_list_obj.values())
                    all_exp_id_list_values=list(all_exp_list_obj.values_list("id",flat=True))
                    print("all_exp_id_list_values",all_exp_id_list_values)
                    # print("all_exp_list_values",all_exp_list_values)
                    exp_wrt_statuscode[code[1]]=all_exp_list_values
                    for bar in all_exp_id_list_values:
                        print("var",bar)
                        exp_obj=exp.objects.get(id=bar)
                        ExpCritObj=ExpCriteriaOrder.objects.filter(exp=exp_obj)
                        foo_dict[bar]=list(ExpCritObj.values_list("pCriteria","pCriteria__criteria_name","sh_hd"))
                    print("foo_dict",foo_dict)
                    crit_exp_wrt_statuscode[code[1]]=foo_dict



                    print("crit_exp_wrt_statuscode",crit_exp_wrt_statuscode)
                    
                    

                # print(exp_wrt_statuscode)


            data={
                "Success":"Sucess",
                "statusCode_list":statusCode_list,
                "exp_wrt_statuscode":exp_wrt_statuscode,
                "crit_exp_wrt_statuscode":crit_exp_wrt_statuscode

            }
            return JsonResponse(data)
        else:
            userobj=User.objects.get(pk=request.user.id)
            role=userobj.role_id_id
            roleobj=Role.objects.get(pk=role)
            role=roleobj.role_name
            if role=='Super_Admin':
                exp_wrt_statuscode={}
                statusCode_list=exStatusCd.objects.values_list("status_code","status_name").distinct()
                statusCode_list=list(statusCode_list)
                print(statusCode_list)
                for code in statusCode_list:
                    print(code[0])
                    print(code[1])
                    exStatusCd_index=exStatusCd.objects.get(status_code=code[0])
                    all_exp_list = exp.objects.filter(status_code=exStatusCd_index)
                    exp_wrt_statuscode[code[1]]=all_exp_list
                print(exp_wrt_statuscode)

               
                



            
            data={
                
                'template_sidebar':self.template_sidebar,
            }
            return render(request,self.template_name,data)
    def post(self,request):
        if request.is_ajax():
            updated_detail_wrt_status=request.POST.get('updated_detail_wrt_status')
            updated_detail_wrt_status = json.loads(updated_detail_wrt_status)
            # print(updated_detail_wrt_status)
            global statusCode_list
            global exp_wrt_statuscode
            print("statusCode_list",statusCode_list)
            for code in statusCode_list:
                    # print("AAAA",code[1])
                    for h,m in zip(exp_wrt_statuscode[code[1]],updated_detail_wrt_status[code[1]]):
                        
                        
                        if h['status']!=m['status']:
                            print(h['status'])
                            print("--------------")
                            print(m['status'])
                            print("status different ")
                            print("m['status_code_id']",m['status_code_id'])
                            exStatusCdObj=exStatusCd.objects.get(status_code=m['status_code_id'])
                            exp.objects.filter(id=h['id']).update(status=m['status'],status_code_id=exStatusCdObj.id,desc=m["desc"])
                        elif h['desc']!=m['desc']:
                            print("description different ")

                            print("m['status_code_id']",m['status_code_id'])
                            exStatusCdObj=exStatusCd.objects.get(status_code=m['status_code_id'])
                            
                            exp.objects.filter(id=h['id']).update(status=m['status'],status_code_id=exStatusCdObj.id,desc=m["desc"])

                        # IF J.STATUS CODE, STATUS OR DESCRIPTION IS DIFFERENT FROM THE DICT SEND THROUGH AJAX THEN UPDATE THE J. 
            
            
            # UPDATING crit_exp_wrt_statuscode
            # 
            statusCode_list=exStatusCd.objects.values_list("status_code","status_name").distinct()
            statusCode_list=list(statusCode_list)
            print(statusCode_list)                    
            exStatusCd_index=exStatusCd.objects.get(status_code=11)

            

            for code in statusCode_list:
                foo_dict={}
                temp_dict={}
                print(code[0])
                print(code[1])
                # code[0] contains the index and code[1] name of the status
                exStatusCd_index=exStatusCd.objects.get(status_code=code[0])
                all_exp_list_obj = exp.objects.filter(status_code=exStatusCd_index)
                all_exp_id_list_values=list(all_exp_list_obj.values_list("id",flat=True))
                print("all_exp_id_list_values",all_exp_id_list_values)
                for bar in all_exp_id_list_values:
                    print("var",bar)
                    exp_obj=exp.objects.get(id=bar)
                    ExpCritObj=ExpCriteriaOrder.objects.filter(exp=exp_obj)
                    foo_dict[bar]=list(ExpCritObj.values_list("pCriteria","pCriteria__criteria_name","sh_hd"))
                    print("foo_dict",foo_dict)
                crit_exp_wrt_statuscode[code[1]]=foo_dict
                print("crit_exp_wrt_statuscode",crit_exp_wrt_statuscode)
            data={
                "crit_exp_wrt_statuscode":crit_exp_wrt_statuscode,
                "Success":"Sucess"
            }
        return JsonResponse(data)
def getSpecificMobileData(request):
    if request.is_ajax():
        if request.method=="POST":
            specsmobdata = request.POST.get('specsmobdata')
            
            specsmobdata = json.loads(specsmobdata)
            print("specsmobdata",type(specsmobdata))
            specmob_dic={}
            for key,val in specsmobdata.items():
                print(key,val)
                specmobret=mobilephones.objects.filter(id__in=val)
                specmobret = list(specmobret.values())   
                specmobret_str=specmobret
                specmob_dic[key]=specmobret_str
            # print("specsmobdata",specmobret)
            print(specmob_dic)
            
            # specmobret = list(specmobret.values())   
            # specmobret_str=specmobret
            return JsonResponse(
            {  'mobilephones':specmob_dic}
            )
catalogcrit_show_list=[]

def getMobiledata(request):
    if request.is_ajax():
        if request.method=="GET":
            print("GET MOBILE DATA")
            # IF BLOCK HAS P.1/P.0 or P.Default then fetch Mobile data from selected admins.
            
            # Assuming P.Default is active
            userobj=User.objects.get(pk=request.user.id)
            role=userobj.role_id_id
            roleobj=Role.objects.get(pk=role)
            role=roleobj.role_name
            pagevisited="false"

            if role=='Super_Admin':
                # // This is the default code to retrieve all
                mobiles_retrieved=mobilephones.objects.all().order_by('-id')
                mobiles_retrieved = list(mobiles_retrieved.values())   
                mobiles_retrieved_list=mobiles_retrieved
                #///////////////////////
            elif role=='Subject':
                flag="false"
                global exp_feat_levels

                exp_list = userobj.subject_set.values_list('exp', flat=True) 
                # Getting the status codes that are active.
                exStatusCd_list=exStatusCd.objects.filter(status_code__gte=11)
                # Fetching that the experiments who has status code as active for the user/subject. 
                inner_qs = exp.objects.filter(id__in=list(exp_list),status_code__in=exStatusCd_list)
                # Using the experiment list for display
                print("inner_qs",list(inner_qs.values('id'))[0]['id'])
                explist=inner_qs.values('id')
                print("explst",explist)
                # Now we know how many experiments the subject is invovled. 
                # For now we'll hard code to get one subject having one active exp... 
                print(exp_under_test)
                exp_obj=exp.objects.get(id=exp_under_test)
                Sub_obj=Subject.objects.get(user=userobj,exp=exp_obj)
                print("blocks",Sub_obj.block.levels_set)
                datetime.datetime.now()
                print("storeuserpagelogs",storeuserpagelogs)
                if "mobile" in storeuserpagelogs:
                    reviseability = [idx for idx in exp_feat_levels if idx.startswith("R.")] 
                    print("res -- R",reviseability[0])
                    if reviseability[0]=="R.0":
                        flag="true"
                        pagevisited=flag

                else:
                    pagevisited=flag
                    storeuserpagelogs["mobile"]=[datetime.datetime.now(),exp_under_test,request.user.id]
                
                # phoneobjs=selectedAdminPhones.objects.filter(exp=exp_obj)

                if 'P.All' not in exp_feat_levels:
                    print("pset id not P.All")
                    # print(phoneobjs)
                    # plist=[]
                    # for pob in phoneobjs:
                    #     print(pob)
                    #     plist.append(pob.mob.id)
                    # # print(plist)
                    # mobiles_retrieved=mobilephones.objects.filter(pk__in=plist)
                    # mobiles_retrieved = list(mobiles_retrieved.values())   
                    # mobiles_retrieved_list=mobiles_retrieved
                    # print("filt_mobiles",filt_mobiles)
                    res = [idx for idx in Sub_obj.block.levels_set if idx.startswith("P.")]
                    print("res",res)
                    if res:
                        # seeing the block e.g/ P.default,P.0,P.1,P.2 send the query
                        phoneobjs=selectedAdminPhones.objects.filter(exp=exp_obj,pset_id__in=res).order_by("-id")
                        mobiles_retrieved = list(phoneobjs.values_list('mob',flat=True))   
                        mobiles_retrieved=list(mobilephones.objects.filter(id__in=mobiles_retrieved).values())
                        mobiles_retrieved_list=mobiles_retrieved
                    else:
                        mobiles_retrieved=mobilephones.objects.all().order_by('-id')
                        mobiles_retrieved = list(mobiles_retrieved.values())   
                        mobiles_retrieved_list=mobiles_retrieved
                  
                else:
                    print("pset id  P.All")

                    mobiles_retrieved= mobilephones.objects.all() 
                    mobiles_retrieved = list(mobiles_retrieved.values())   
                    mobiles_retrieved_list=mobiles_retrieved


                # print(mobiles_retrieved_list)
            # // This is the default code to retrieve all
            # mobiles_retrieved=mobilephones.objects.all().order_by('-id')
            # mobiles_retrieved = list(mobiles_retrieved.values())   
            # mobiles_retrieved_list=mobiles_retrieved
            #///////////////////////
            cat_obj=criteria_catalog_disp.objects.get(id=1)
            catalogcrit_show_list=cat_obj.catalog_crit_display_order
            return JsonResponse(
                {   "pagevisited":pagevisited,
                    'mobilephones':mobiles_retrieved_list,
                    'catalogcrit_show_list':catalogcrit_show_list,

                }
            )
def getReqPhones(request):
    if request.method=="POST":
        if request.is_ajax:
            brandname=request.POST.get("brands")
            brandname = json.loads(brandname)
            price_range=request.POST.get("price")
            price_range = json.loads(price_range)

            print ("brand name",brandname)

            print ("price_range",price_range)
            # fetch mobile phones based on these... 
            if not brandname:
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range[0], price_range[1])).order_by('id') 
            else:
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range[0], price_range[1]),Brand__in=brandname).order_by('id') 

            print("MOBILES RETR")
            print(mobiles_retrieved)
            listofmob=list(mobiles_retrieved.values())
            print("list of mob",listofmob)
            data={
                'mobilephones':listofmob
            }
            return JsonResponse(data)
def retSpecMobilePhone(request):

    if request.method=="POST":
        if request.is_ajax:
            mobile_id=request.POST.get("mobile_id") 
            # based on mobile id ret phone from mobilephones model.
            print("mobile_id",mobile_id) 
            mobile=mobilephones.objects.get(id=mobile_id)
            phone=mobile.Mobile_Name
            
            data={
                "phone":phone
            }
            return JsonResponse(data)

def SavePhoneSets_P0(request):
    if request.method=="POST":
        if request.is_ajax:
            print("P0 here")
            
            expCont = getExpController(request)
            print("Return from getExpController")
            existExpId = expCont.exp.id
            exp_obj=Experiment.objects.get(custom_exp_id=expCont.exp.custom_exp_id)

            if (selectedAdminPhones.objects.filter(exp=exp_obj).exists()):
                selectedAdminPhones.objects.filter(exp=exp_obj).delete()          
            
            expPSets = selectedAdminPhones()
            expPSets.exp = expCont.exp
            expPSets.pset_id= "P.All"
            # expPSets.mob = p_set.get(id=m)
            expPSets.p_order = 0
            expPSets.save()
            data = {
                    "data":"data",
                     'exp_id':existExpId,
                     'custom_exp_id':expCont.exp.custom_exp_id,
                     
                }
            return JsonResponse(data)

def SavePhoneSets(request):
     if request.method=="POST":
            if request.is_ajax:
                phoneset_dic = request.POST.get('phoneset_dic')
                phoneset_dic=json.loads(phoneset_dic)
                featlevels_dic=request.POST.get('featlevels_dic')
                postedFLevels = json.loads(featlevels_dic)
                expCont = getExpController(request)
                existExpId = expCont.exp.id
              
                print("existExpId",existExpId)

                expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                block_set = expCont.generateBlocks()
                block_list = list(block_set.all().values('serial_no','levels_set'))
                print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                print(block_list)
                p_levList = list()
                print("P>DEF",phoneset_dic)
                if 'P.Default' in phoneset_dic.keys():
                    print("PHONESET DICT--<",phoneset_dic)
                    exp_obj=Experiment.objects.get(custom_exp_id=expCont.exp.custom_exp_id)
                    # if (selectedAdminPhones.objects.filter(exp=exp_obj).exists()):
                    #     selectedAdminPhones.objects.filter(exp=exp_obj).delete()
                    
                    for key,s in phoneset_dic.items():
                        print(key,":",s)
                        p_set = mobilephones.objects.filter(id__in=s)
                        p_levList.append('P.'+str(key))
                        for count, i in enumerate(s):
                            expPSets = selectedAdminPhones()
                            expPSets.exp = expCont.exp
                            expPSets.pset_id= key
                            expPSets.mob = p_set.get(id=i)
                            expPSets.p_order = count
                            expPSets.save()

                else:
                    exp_obj=Experiment.objects.get(custom_exp_id=expCont.exp.custom_exp_id)
                    # Updation check. 
                    if (selectedAdminPhones.objects.filter(exp=exp_obj).exists()):
                        sap_objs=selectedAdminPhones.objects.filter(exp=exp_obj)
                        pset_list=set(sap_objs.values_list('pset_id', flat=True))
                        pset_list=list(pset_list)
                        # pset_list=['P.1','P.2','P.3']

                        print("pset_list",pset_list)
                        keylist=list(phoneset_dic.keys())
                        # keylist=['P.1','P.2']
                        print("keylist",keylist)
                        if (len(pset_list)>len(keylist)):
                            diff_list=list(set(pset_list) - set(keylist))
                            obj=selectedAdminPhones.objects.filter(exp=exp_obj,pset_id__in=diff_list).delete()
                            print("object",obj)
                            print('Difflist for db deletion',diff_list)
                        elif (len(pset_list)<len(keylist)):
                            diff_list=list(set(keylist) - set(pset_list))
                            print('Difflist for db updation',diff_list)
                            
                            for i in diff_list:
                                p_set = mobilephones.objects.filter(id__in=phoneset_dic[i])

                                for count, m in enumerate(phoneset_dic[i]):
                                    expPSets = selectedAdminPhones()
                                    expPSets.exp = expCont.exp
                                    expPSets.pset_id= i
                                    expPSets.mob = p_set.get(id=m)
                                    expPSets.p_order = count
                                    expPSets.save()
                                

                            
                        dum_dict={}
                        for sap in sap_objs:
                            
                        # after checking if phones for exp under construction exsists
                        # we have to get each phone obj check its pset_id and phone name/id and update its position.
                            
                            for key,s in phoneset_dic.items():
                                sp=selectedAdminPhones.objects.filter(exp=exp_obj,pset_id=key)
                                sp_list=list(sp.values_list('mob',flat=True))
                                print("sp",sp.count())
                                splen=sp.count()
                                print("SAP",sap.pset_id)
                                print("mob",sap.mob.id)
                                print('key',key)
                                print("s",s)
                                print("splen",splen)
                            

                                if ((sap.mob.id in s) and sap.pset_id==key ):
                                    
                                    print("s.index(sap.mob.id)",s.index(sap.mob.id))
                                    sap.p_order=s.index(sap.mob.id)
                                    sap.save()
                                    if key in dum_dict.keys(): 
                                        print("sap.mob.id",sap.mob.id)
                                        print("key",key)
                                        dum_dict[key].append(sap.mob.id)
                                        print("DUM_DUCT",dum_dict)
                                    
                                    else:
                                        print("SHould Run only once for keys... ")
                                        dum_dict[key]=[]
                                        dum_dict[key].append(sap.mob.id)
                                        

                                elif (sap.mob.id not in s) and (sap.pset_id==key) and (splen>len(s)):
                                    print("length Greater delete")
                                    obj=selectedAdminPhones.objects.filter(exp=exp_obj,pset_id=key,mob=sap.mob.id).delete()
                                if key in dum_dict.keys(): 
                                    if ((len(dum_dict[key])==splen) and (splen<len(s))  and (sap.pset_id==key)):
                                        temp_list=[]
                                        temp_list=dum_dict[key]

                                        diff_list=set(s)-set(temp_list)
                                        print("UP_DIFF",diff_list)
                                        for i in diff_list:
                                            p = mobilephones.objects.get(id=i)
                                            pos=s.index(i)

                                            expPSets = selectedAdminPhones()
                                            expPSets.exp = expCont.exp
                                            expPSets.pset_id= key
                                            expPSets.mob = p
                                            expPSets.p_order = pos
                                            expPSets.save()
                                            # print("FOR Updation")
                                            # print("KEY")
                                            # expPSets=selectedAdminPhones()
                                            # expPSets.exp = expCont.exp
                                            # expPSets.pset_id= key
                                            # expPSets.mob = mobilephones.objects.get(id=sap.mob.id)
                                            # expPSets.p_order = s.index(sap.mob.id)
                                            # expPSets.save()
                                print("dum_dict",dum_dict)

                                print("----------------------------------------------")
                        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                                
                    else:
                        for key,s in phoneset_dic.items():
                            print(key,":",s)
                            p_set = mobilephones.objects.filter(id__in=s)
                            p_levList.append('P.'+str(key))
                            for count, i in enumerate(s):
                                expPSets = selectedAdminPhones()
                                expPSets.exp = expCont.exp
                                expPSets.pset_id= key
                                expPSets.mob = p_set.get(id=i)
                                expPSets.p_order = count
                                expPSets.save()
                    # A Check is to be made for updation...
                        # for key,s in phoneset_dic.items():
                        #     p_set = mobilephones.objects.filter(id__in=s)
                        #     print("p_set",p_set)
                        #     p_levList.append('P.'+str(key))
                        #     print("key",key)
                        #     print("s",s)
                        #     for count, p in enumerate(p_set):
                        #         print("p",p)
                        #         print("count",count)
                        #         expPSets = selectedAdminPhones()
                        #         expPSets.exp = expCont.exp
                        #         expPSets.pset_id= key
                        #         expPSets.mob = p
                        #         expPSets.p_order = count 
                        #         expPSets.save()
                    # print(selectedAdminPhones.objects.filter(exp_id = expCont.exp.id))       
                    




                data = {
                    "data":"data",
                     'exp_id':existExpId,
                     'custom_exp_id':expCont.exp.custom_exp_id,
                     'block_list':block_list
                }
                return JsonResponse(data) #, safe=False)

def SaveCurrentSubjExp(request):
    if request.method=="POST":
        if request.is_ajax:
            global exp_under_test
            exp_under_test= request.POST.get('exp_num')
            exp_under_test=json.loads(exp_under_test)
            print("exp_under_test",exp_under_test)
            data={"success":"success"}
            return JsonResponse(data)

def deleteSelectedAdminPhones(request):
     if request.method=="POST":
        if request.is_ajax:
            exp_id= request.POST.get('exp_id')
            print("*******************************************************")
            print("eEXPID",exp_id)
            print("*******************************************************")
            exp_obj=exp.objects.get(id=exp_id)
            selectedAdminPhones.objects.get(exp=exp_obj).delete()
            data={}
            return JsonResponse(data)


def submitData(request):
    global critw_logs_dict
    if request.method=="POST":
        if request.is_ajax:
            storehoveronbarlog= request.POST.get('storehoveronbarlog')
            storehoveronbarlog=json.loads(storehoveronbarlog)


            storehoveronpielog= request.POST.get('storehoveronpielog')
            storehoveronpielog=json.loads(storehoveronpielog)

            alt_crit_logs_dict= request.POST.get('alt_crit_logs_dict')
            alt_crit_logs_dict=json.loads(alt_crit_logs_dict)

            storenextprevbuttonlogs=request.POST.get('storenextprevbuttonlogs')
            storenextprevbuttonlogs=json.loads(storenextprevbuttonlogs)
            # print("storehoveronbarlog",storehoveronbarlog)
            # print("storehoveronpielog",storehoveronpielog)
            # print("alt_crit_logs_dict",alt_crit_logs_dict)
            # print("storenextprevbuttonlogs",storenextprevbuttonlogs)


           
            for key in storehoveronbarlog:
                print("key",key)
                print("storehoveronpielog[key][0]",storehoveronbarlog[key][0])
                print("storehoveronpielog[key][1]",storehoveronbarlog[key][1])
                print("storehoveronpielog[key][2]",storehoveronbarlog[key][2])

                # userid=storehoveronbarlog[key][0]
                shbcl_obj=StoreHoverBarChartLogs()
                shbcl_obj.value=storehoveronbarlog[key][1]
                shbcl_obj.user=User.objects.get(id=request.user.id)
                shbcl_obj.phone_name=storehoveronbarlog[key][2]
                shbcl_obj.time=key
                shbcl_obj.save()
            for key in storehoveronpielog:
                print("key",key)
                print("storehoveronpielog[key][0]",storehoveronpielog[key][0])
                print("storehoveronpielog[key][1]",storehoveronpielog[key][1])
                print("storehoveronpielog[key][2]",storehoveronpielog[key][2])

                # userid=storehoveronbarlog[key][0]
                shpcl_obj=StoreHoverPieChartLogs()
                shpcl_obj.value=storehoveronpielog[key][2]
                shpcl_obj.user=User.objects.get(id=request.user.id)
                shpcl_obj.criteria_name=storehoveronpielog[key][1]
                shpcl_obj.time=key
                shpcl_obj.save()
            for key in storenextprevbuttonlogs:
                print("key",key)
                print("storenextprevbuttonlogs[key][0]",storenextprevbuttonlogs[key][0])
                print("storenextprevbuttonlogs[key][1]",storenextprevbuttonlogs[key][1])
                print("storenextprevbuttonlogs[key][2]",storenextprevbuttonlogs[key][2])

                # userid=storehoveronbarlog[key][0]
                snpbcl_obj=StoreNextPrevButtonLogs()
                snpbcl_obj.button_name=storenextprevbuttonlogs[key][0]
                snpbcl_obj.user=User.objects.get(id=request.user.id)
                snpbcl_obj.phone_name=storenextprevbuttonlogs[key][2]
                snpbcl_obj.time=key
                snpbcl_obj.save()
            print("critw_logs_dict",critw_logs_dict)
            # for key in critw_logs_dict:
            #     scwl_obj=StoreCritWeightLogs()
            #     scwl_obj.value=critw_logs_dict[key][1]
            #     scwl_obj.user=User.objects.get(id=request.user.id)
            #     scwl_obj.criteria_name=key
            #     scwl_obj.time=critw_logs_dict[key][2]
            #     scwl_obj.save()
            data={}
            return JsonResponse(data)




class createSurveyForm(TemplateView):
    template_name='webapp/crudexperiment/survey_form.html'
    def get(self,request):
        data={}
        return render(request,self.template_name,data)

    def post(self,request):
        pass
class saveSurveyForm(TemplateView):
    def get(self,request):
        data={}
        pass
    def post(self,request):
        if request.method=='POST':
            main_dict=request.POST.get('main_dict')
            main_dict=json.loads(main_dict)
            print("main_dict",main_dict)

            survey_obj=surveyForm()
            print("ssss")
            survey_obj.surveydata=json.dumps(main_dict)
            survey_obj.save()
        data={}
        return JsonResponse(data)

    