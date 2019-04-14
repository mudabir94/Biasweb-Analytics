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
from biasweb.pythonscripts.insertcsvfiletotable import populate_Table
from biasweb.utils.assign import Assigner

#loading forms from forms.py file. 
from .forms import (NameForm, SignUpForm, blogForm, filterform,
                    mobile_phone_form, sort_filter_form)
#-----------------------------------------------------------------
from .models import Role, User, blog
from .models import experiment as exp
from .models import (mobile_phone, mobilephones, platform_feature, prunedmobilephones,
                     samsung_phone, sort_feature, userscoreRecord,ExpCriteriaOrder)
from.models import template_roles as tr 
from. models import templates as tpl

from .models import selectedAdminPhones

#--------------------------------------------------------------------------------------------------
role=1   #global variable used in adminsetup and globalFunc function. 
#mobiles=samsung_phone.objects.raw('SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2') # making mobiles object global.
# mobiles=mobilephones.objects.raw('SELECT * FROM webapp_mobilephones WHERE id=1 or id=2') # making mobiles object global.
mobiles=None
filter_flag=None
sizeofmob=0 # global variable assigned in filter class.
filt_mobiles=None
#-------------------------------------------------------------------------------------------------

            
@method_decorator(login_required, name='dispatch')
class Home(TemplateView):
    template_name='webapp/home.html'
    def get(self,request):
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
            # return redirect('/filtered_mobile_view')
            # return render(request,'webapp/2by2comparemobilespecs.html')
            # return render(request,template_sidebar)
        elif role=='Experiment_Admin':
            # roleobj=Role.objects.get(pk=role)
            # role_name=roleobj.role_name
            # print(role_name)
            template_sidebar='webapp/sidebartemplates/sidebartemp_expadm.html'
            
        elif role=='Platform_Admin':
            roleobj=Role.objects.get(pk=role)
            role_name=roleobj.role_name
            print(role_name)
            template_sidebar='webapp/sidebartemplates/sidebartemp_pltfadm.html'
        elif role=='Subject':
            # all other conditions of subjects will be done here. 
            
            return render(request,'webapp/2by2comparemobilespecs.html')
            # return redirect('/filtered_mobile_view')

        #*****************************************************
        return render(request,self.template_name,{'role_id':userobj.role_id_id,'template_sidebar':template_sidebar})
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



def showMob(request):
    if request.method=="POST":
        if request.is_ajax:
        # print("ajax",request.POST.get('data'))
            ####print("PST",request.POST.get('d')) 
            mobiledata = request.POST.get('mobiledata')
        ### print('JSONLOADS',eval(d))
            mobiledata_json = json.loads(mobiledata)
            print("mobiledata_json",mobiledata_json[0])
            query_array=[]
            count=1    
            for key,value in  enumerate(mobiledata_json):
                print("key",key)
                print ("val", value)
                # query_array.append(' '+ 'id'+ '=' + value )
                query_array.append(value)
            #query=samsung_phone.objects.filter(id__in=(query_array))
            query=mobilephones.objects.filter(id__in=(query_array))
                        # old_query = 'SELECT * FROM webapp_samsung_phone WHERE '+ ' or ' .join(query_array)
            global comp_mobiles
            global sizeofmob
                # mobiles=samsung_phone.objects.raw(query)
            comp_mobiles=query
            size_of_mobile=len(list(comp_mobiles))
            sizeofmob=size_of_mobile
            print(comp_mobiles)
            dict = {'size_of_mobile':size_of_mobile}
    return HttpResponse(json.dumps(dict))
    #return render_to_response(request,'webapp/showmob.html',{'mobiles':mobiles}) 
    '''
    query = 'SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2'
    mobiles=samsung_phone.objects.raw(query)
    print(mobiles)
    return render(request,'webapp/showmob.html',{'mobiles':mobiles})
    '''
def compareMobileSpecsFilterVer(request):
    if request.method=="GET":
        return render(request,'webapp/2by2comapremobilespecsfiltver.html')
    if request.method=="POST":
        if request.is_ajax: 
            mobile={}
            allmobile={}
            global comp_mobiles
            alternative_list=[]
            criteria_list=['imagepath1','price',"Resolution"]
            
            test_mobiles = comp_mobiles
            
            for m in test_mobiles:
                print('m objest',m)
                for crit in criteria_list:
                    print(crit)
                    mobile[crit]=getattr(m, crit)
                mobile['Others']=m.Mobile_Name

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
    
feature_to_display=''
feature_to_hide=''
class orderCriteria_Setup(TemplateView):
    def get(self,request):
        role_name=['']
        print(request.user.id)
        userobj=User.objects.get(pk=request.user.id)
        print("user object",userobj.role_id_id)
        role_id=userobj.role_id_id
        roleobj=Role.objects.get(pk=role_id)
        role=roleobj.role_name
        print(role)
        if  request.is_ajax():
            feature_to_display=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role_id).order_by('position')
            print("feature",feature_to_display)
            feature_to_hide=sort_feature.objects.filter(Q(sh_hd = 0),roles=role_id).order_by('position')    
            print("feature2",feature_to_hide)
            feature_to_display = list(feature_to_display.values())
            feature_to_hide = list(feature_to_hide.values())

            data={
                'feature_to_display':feature_to_display,
                'feature_to_hide':feature_to_hide,
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
                expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                block_set = expCont.generateBlocks()
                block_list = list(block_set.all().values('serial_no','levels_set'))
                print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
                print(block_list)
                # save orderset Details in expCriteriaOrder
                exp_obj=Experiment.objects.get(custom_exp_id=existCusId)
                
                p_levList=list()
                for key,s in crit_order_dict.items():
                        print(key,":",s)
                        # o_set = mobilephones.objects.filter(id__in=s)

                        p_levList.append('CO.'+str(key))
                        for count, i in enumerate(s):
                           
                            print("count",count)
                            print("ii",i)
                            expOSets=ExpCriteriaOrder()
                            expOSets.exp=expCont.exp
                            expOSets.cOrder_id=key
                            expOSets.pCriteria=i
                            expOSets.position=count+1
                            expOSets.sh_hd=1
                            expOSets.save()
                            # expPSets = selectedAdminPhones()
                            # expPSets.exp = expCont.exp
                            # expPSets.pset_id= key
                            # expPSets.mob = p_set.get(id=i)
                            # expPSets.p_order = count
                for key,s in crit_hide_dict.items():
                        print(key,":",s)
                        # o_set = mobilephones.objects.filter(id__in=s)

                        p_levList.append('CO.'+str(key))
                        for count, i in enumerate(s):
                           
                            print("count",count)
                            print("ii",i)
                            expOSets=ExpCriteriaOrder()
                            expOSets.exp=expCont.exp
                            expOSets.cOrder_id=key
                            expOSets.pCriteria=i
                            expOSets.position=0
                            expOSets.sh_hd=0
                            expOSets.save()
                            # expPSets = selectedAdminPhones()
                            # expPSets.exp = expCont.exp
                            # expPSets.pset_id= key
                            # expPSets.mob = p_set.get(id=i)
                            # expPSets.p_order = count
                            
                data={
                'success':'success',
                'exp_id':existExpId,
                'custom_exp_id':expCont.exp.custom_exp_id,
                'block_list':block_list
                }
                return JsonResponse(data)
              
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

class showFilter(TemplateView):
    def get(self,request):
        print("in filter")    
        print("global",role)
        # mobiles=samsung_phone.objects.all()
        mobiles=mobilephones.objects.all()
        # m=samsung_phone.objects.all()
        m=mobilephones.objects.all()
        feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')

        Colors=['black','white','gold']
        OS=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
        'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
        Size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
        Cpu=['octa-core','quad-core']
        back_camera=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
        battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
        return render(request,'webapp/filter_test.html',{'mobiles':mobiles,'Colors':Colors,
        'os':OS,'size':Size,'feat':feat,'cpu':Cpu,'back_cm':back_camera,'battery':battery})
filter_features=[]
class filter(TemplateView):
   
    def get(self,request):
        global filter_features
        if request.is_ajax():
            print("IN AJAX REQUEST")
            all_data_dic={}
            price=['100000','120000']
            Size=['5','5.5','5.3','6.5','7']
            Colors=['black','white','gold']
            OS=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
            'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
            # size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
            Cpu=['octa-core','quad-core']
            backcam=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
            battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
            mobilecompany=['samsung','I Phone']
            Chip=['Exynos 9810 Octa','Exynos 8895 Octa','Qualcomm Snapdragon 805','Exynos8890Octa','Quad-core (2 x 2.15 GHz Kryo + 2 x 1.6 GHz Kryo)','Exynos 7885 Octa','QualcommMSM8996Snapdragon820','Exynos7420','Exynos 7420 Octa','Exynos 7880 Octa','QualcommMSM8953Snapdragon625','Mediatek MT6757 Helio P20','Exynos 7870 SoC','Exynos 7870','1.4 GHz Quad-Core Cortex-A53','QualcommMSM816Snapdragon410','QualcommMSM8917Snapdragon425','1.2 GHz Quad-core Cortex-A53','Spreadtrum SC9830','MediatekMT6737T','Exynos3475','Spreadtrum SC9830','Spreadtrum','','']
            resolution=['720 x 1280','540 x 960','480 x 800','1440 x 2960','1080 x 2220','1080 x 1920']      
            weight=['163','195','173','174','155','191','157','172','132','0','181','169','179','135','160','170','143','159','146','156','138','131','122','126','153']  
            dimensions=['147.6 x 68.7 x 8.4 mm','162.5 x 74.6 x 8.5 mm','159.5 x 73.4 x 8.1 mm','151.3 x 82.4 x 8.3 mm','148.9 x 68.1 x 8 mm','159.9 x 75.7 x 8.3 mm','150.9 x 72.6 x 7.7 mm','149.2 x 70.6 x 8.4 mm','143.4 x 70.8 x 6.9 mm','142.1 x 70.1 x 7 mm','153.2 x 76.1 x 7.6 mm','156.8 x 77.6 x 7.9 mm','146.1 x 71.4 x 7.9 mm','152.4 x 74.7 x 7.9 mm','146.8 x 75.3 x 8.9 mm','146.8 x 75.3 x 8.9 mm','156.7 x 78.8 x 8.1 mm','135.4 x 66.2 x 7.9 mm']
            all_data_dic['price']=price
            all_data_dic['Size']=Size
            all_data_dic['Colors']=Colors
            all_data_dic['OS']=OS
            all_data_dic['Cpu']=Cpu
            all_data_dic['backcam']=backcam
            all_data_dic['battery']=battery

            filter_features = list(filter_features.values())
            print(":filter",filter_features)
            data_filter_feature={}
            for i in filter_features:
                print("i:",i['feature'])
                data_filter_feature[i['feature']]=all_data_dic[i['feature']]

            data={
                'feat':filter_features,
                'data_filter_feature':data_filter_feature
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
                roles=1
                filter_features=sort_feature.objects.filter(~Q(sh_hd = 0),roles=roles).order_by('position')
                # feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=roles).order_by('position')

                ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=roles).order_by('position')
                print("In super admin",filter_features)
            elif role=='Subject':
                # global role
                roles=2
                filter_features=sort_feature.objects.filter(~Q(sh_hd = 0),roles=roles).order_by('position')
                ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=roles).order_by('position')
            # else:
            #     print("in mobile redirect")
            #     return redirect('/mobileanl/mobile')

            return render(request,'webapp/filter_test.html')
    
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
            d = request.POST.get('filt_opt_sel')
            #print('d',d)
            filt_opt_sel = json.loads(d)
            # print("filt_opt_sel",filt_opt_sel)
            filter_d=filt_opt_sel
            # return render(request,'webapp/mobile.html')  
            data={'success':"success"}
            


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
            print("sizeofmob",sizeofmob)
            return JsonResponse(data)

            
          
            
        # return render(request,'webapp/mobile.html',{'mobiles':mobiles})
        # return redirect('/mobile')


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
                # print("mobiles",filt_mobiles)
                uid = request.user.username
                print(uid)
                tuser = User.objects.get(username=uid)
                exp_list = tuser.subject_set.values_list('exp', flat=True) #PLEASE CHECK IF WE CAN GET PREFETCH RELATED HERE
                exp_active = max(exp_list)                
                phoneobjs=selectedAdminPhones.objects.filter(exp=exp_active)
                # print(phoneobjs)
                plist=[]
                for pob in phoneobjs:
                    print(pob)
                    plist.append(pob.mob.id)
                # print(plist)
                filt_mobiles=mobilephones.objects.filter(pk__in=plist)
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
            page = request.GET.get('page')
            ex_mobiles = paginator.get_page(page)
            template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
            return render(request,self.template_name,{'mobiles':ex_mobiles,'template_sidebar':template_sidebar,'role':"Super_Admin"})
        elif role=='Subject':
            
            mobiles= mobilephones.objects.all() 
            paginator = Paginator(mobiles,9)
            page = request.GET.get('page')
            ex_mobiles = paginator.get_page(page)
            template_sidebar='webapp/sidebartemplates/sidebartemp_superadmin.html'
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
        sess_expId = request.session['sess_expId']
        print('SESSION ID',sess_expId)
    except KeyError:
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
        expAdminId = request.user.custom_id
        print('expAdminId',expAdminId)
        expCont = ExperimentController(a_id=expAdminId)
        print('NEW Exp id',expCont.exp.id)
        request.session['sess_expId'] = expCont.exp.id
        request.session['sess_custExpId'] = expCont.exp.custom_exp_id
        print('request.session',request.session['sess_custExpId'] )
        print("SAVED NEW EXPERIMENT TO SESSION---->>>>>>")

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
    try:
        filepath = Path("C:/biasweb/expCont4.p")
    except FileNotFoundError:
        filepath=None
    else:
        if filepath.exists():
            os.remove('C:/biasweb/expCont4.p')
        if request.session['sess_expId']:
            del request.session['sess_expId']
        return HttpResponse()


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

class createExperiment(TemplateView): 
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
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range_values[0], price_range_values[1])).order_by('id') 
            else:
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range_values[0], price_range_values[1]),Mobile_Companny__in=brandnames).order_by('id') 


            
            # else: 
            #     mobiles_retrieved=samsung_phone.objects.filter(price_in_pkr__range=(10000, 30000))
            # print("mobiles_retrieved",mobiles_retrieved)

            # print(mobiles_retrieved) 
            mobiles_retrieved = list(mobiles_retrieved.values())
            # samsung_phones=mobiles_retrieved
            mobilephones_str=mobiles_retrieved
            # print("mobilephones_str",mobilephones_str)
            print("price_range",price_range)
            return JsonResponse(
            {  
                # 'samsung_phones':samsung_phones
                'mobilephones':mobilephones_str,
                "price_range_values":price_range
            }
            )
            
        else:
            print("NOT AJAX")
            # samsung_phones= samsung_phone.objects.all()
            
            m_p= mobilephones.objects.all() 
            # print("mobile_phones",m_p)
            # paginator = Paginator(samsung_phones,9)
            paginator = Paginator(m_p,9)
            page = request.GET.get('page')
            # samsung_phones = paginator.get_page(page)
            mobile_phones__str = paginator.get_page(page)

        
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
            try:
                sess_expId = request.session['sess_expId']
                print("sesid",sess_expId)
            except KeyError:
                sess_expId = ""
            try:
                sess_custExpId = request.session['sess_custExpId']
            except KeyError:
                sess_custExpId = "123"
            
            return render(request,self.template_name,
            {  'creat_exp_template_sidebar':creat_exp_template_sidebar,
               'creat_exp_template_sidebar2':creat_exp_template_sidebar2,
                'platformfeatobj':platformfeatobj,
                'sess_expId':sess_expId,
                'sess_custExpId':sess_custExpId,
                # 'samsung_phones':samsung_phones
                'mobilephones':mobile_phones__str
                                            }
            )
                                        
                                    
    def post(self,request):
        if request.method=="POST":
            print("====IN CREATEEXP POST METHOD====")
            data = {'data':"data"}

            if request.is_ajax:
                d = request.POST.get('dict')
                print(request.POST.get('price_range_values'))
                #print('d',d)
                postedFLevels = json.loads(d)
                print('postedFLevels',postedFLevels)
                # if postedFLevels is none then remove everything ..... 
                print('b',type(postedFLevels),postedFLevels)
                
                #CREATE EXPERIMENT CONTROLLER AND INITIALIZE
                #returns either a controller for new experiment
                #or for existing one [TODO: CHECK STATUS OF EXPERIMENT AS IN DESIGN_MODE]
                expCont = getExpController(request)
                existExpId = expCont.exp.id
    
                #SET FLEVELS
                expCont.setFSet(newFLevels=postedFLevels,prompt=False)
                block_set = expCont.generateBlocks()
                block_list = list(block_set.all().values('serial_no','levels_set'))
                
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
from webapp.models import experiment as Experiment
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
                print("PHONESET DICT",phoneset_dic)
                # exp_obj=Experiment.objects.get(custom_exp_id="ses-007-0266")
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



class editExperiment(TemplateView):
        def get(self,request):
            # Get user id. 
            # check admin status.
            # fetch all exp created by this admin
            # get the latest exp .. In future only get the exp which has status=active. 
            # userid= request.user.id
            # userobj=user.objects.get(pk=userid)
            uid=request.user.id
            print(uid)
            print(Experiment.objects.filter(owner=uid).values_list('id',flat=True))
            expList=Experiment.objects.filter(owner=uid).values_list('id',flat=True)
            expactive=max(expList)
            print(expactive)
            request.session['sess_expId'] = expactive
            expCont = getExpController(request)
            existExpId = expCont.exp.id
             #SET FLEVELS
            expCont.setFSet(newFLevels=postedFLevels,prompt=False)
            block_set = expCont.generateBlocks()
            block_list = list(block_set.all().values('serial_no','levels_set'))
                
                # # blockStr = "\n".join(str(b) for b in expCont.exp.block_set.all())
            print('<<<<<<TO DISPLAY ON PAGE>>>>>>')
            print(block_list)
            data = {
                    'exp_id':existExpId,
                    'custom_exp_id':expCont.exp.custom_exp_id,
                    'block_list':block_list
                }
            


            
            pass
        def post(self,request):
            pass
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

def getMobiledata(request):
    if request.is_ajax():
        if request.method=="GET":
            mobiles_retrieved=mobilephones.objects.all()
            mobiles_retrieved = list(mobiles_retrieved.values())   
            mobilephones_str=mobiles_retrieved
            return JsonResponse({'mobilephones':mobilephones_str})
            
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
                mobiles_retrieved=mobilephones.objects.filter(price__range=(price_range[0], price_range[1]),Mobile_Companny__in=brandname).order_by('id') 

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

            