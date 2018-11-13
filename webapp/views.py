import codecs
import csv
#-------------------------------------------------------------------------------------------------
#test_experiment imports. 
import itertools
import json
import os
import pickle
from pathlib import Path

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.forms import UserCreationForm
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
from biasweb.experiment.controller import ExperimentController
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
from .models import (mobile_phone, phone, platform_feature, prunedmobilephones,
                     samsung_phone, sort_feature, userscoreRecord)
from.models import template_roles as tr 
from. models import templates as tpl

#--------------------------------------------------------------------------------------------------
role=1   #global variable used in adminsetup and globalFunc function. 
mobiles=samsung_phone.objects.raw('SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2') # making mobiles object global.
sizeofmob=0 # global variable assigned in filter class.
#-------------------------------------------------------------------------------------------------
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
        
        elif role=='Experiment_Admin':
            roleobj=Role.objects.get(pk=role)
            role_name=roleobj.role_name
            print(role_name)
            template_sidebar='webapp/sidebartemplates/sidebartemp_expadm.html'
        elif role=='Platform_Admin':
            roleobj=Role.objects.get(pk=role)
            role_name=roleobj.role_name
            print(role_name)
            template_sidebar='webapp/sidebartemplates/sidebartemp_pltfadm.html'

        #*****************************************************


        return render(request,self.template_name,{'role_id':userobj.role_id_id,'template_sidebar':template_sidebar})
    def post(self,request):

        return render(request,self.template_name)

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


def showMob(request):
    if request.method=="POST":
        if request.is_ajax:
        # print("ajax",request.POST.get('data'))
            ####print("PST",request.POST.get('d')) 
            d = request.POST.get('d')
        ### print('JSONLOADS',eval(d))
            b = json.loads(d)
            print(b[0])
            query_array=[]
            count=1    
            for key,value in  enumerate(b):
                print("key",key)
                print ("val", value)
                query_array.append(' '+ 'id'+ '=' + value )
            query = 'SELECT * FROM webapp_samsung_phone WHERE '+ ' or ' .join(query_array)
            global mobiles
            global sizeofmob
            mobiles=samsung_phone.objects.raw(query)
            som=len(list(mobiles))
            sizeofmob=som
            print(mobiles)
            print("som",som)

            dict = {'som':som}
    return HttpResponse(json.dumps(dict), content_type='application/json')
    #return render_to_response(request,'webapp/showmob.html',{'mobiles':mobiles}) 
    '''
    query = 'SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2'
    mobiles=samsung_phone.objects.raw(query)
    print(mobiles)
    return render(request,'webapp/showmob.html',{'mobiles':mobiles})
    '''
    
     
def cart(request):
    #query = 'SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2 or id=3'
    #mobiles=samsung_phone.objects.raw(query)
    print(mobiles)
    
    return render(request, 'webapp/cart.html',{'mobiles':mobiles,'s':sizeofmob})
def ind(request):
   
    if request.is_ajax:
       # print("ajax",request.POST.get('data'))
        ####print("PST",request.POST.get('d')) 
        d = request.POST.get('d')
       ### print('JSONLOADS',eval(d))
        b = json.loads(d)

        print(b[0])
        count=1
        for key,value in  enumerate(b):
            print(key)
            k=str(int(key)+1)
            print ("test", value,k)
            
            with connection.cursor() as cursor:
                cursor.execute("UPDATE webapp_sort_feature SET position="+str(count)+" WHERE feature='"+value+"' and roles="+str(role)+";") 
                print("executed") 
            count=count+1
        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
        
        #print ("test", d['color'])
        return render(request, 'webapp/admin_setup.html')




def test(request):
   
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
             
            with connection.cursor() as cursor:
                cursor.execute("UPDATE webapp_sort_feature SET sh_hd="+"0"+" WHERE feature='"+value+"' and roles="+str(role)+"; ") 
                print("executed") 
            
        

        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
            
        #print ("test", d['color'])
        return render(request, 'webapp/admin_setup.html')
    
def on(request):
   
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
             
            with connection.cursor() as cursor:
                cursor.execute("UPDATE webapp_sort_feature SET sh_hd="+"1"+" WHERE feature='"+value+"' and roles="+str(role)+" ; ") 
                print("executed") 
            
        

        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
            
        #print ("test", d['color'])
        return render(request, 'webapp/admin_setup.html')
  
    
def globalFunc(request):
   
    if request.is_ajax:
       # print("ajax",request.POST.get('data'))
        ####print("PST",request.POST.get('d')) 
        d = request.POST.get('d')
       ### print('JSONLOADS',eval(d))
        b = json.loads(d)

        print("in func",b)
        print(type(b))
        
        a=int(b)
        print(int(b))
        print(type(a))
        global  role
        role=a

        

        # UPDATE [Table] SET [Position] = $i WHERE [EntityId] = $value 
            
        #print ("test", d['color'])
          
        return render(request, 'webapp/admin_setup.html')

        

        
    

def adminSetup(request):
    global  role
    
    feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
    ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
    colors=['black','white','gold']
    size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
    role_name=['']
    if role==1:
       role_name=['Student']
    elif role==2:
        role_name=['Professor']
    return render(request, 'webapp/admin_setup.html',{'feat':feat,'colors':colors,'role_name':role_name,'size':size,'ft':ft})
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
        mobiles=samsung_phone.objects.all()
        m=samsung_phone.objects.all()
        feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')

        colors=['black','white','gold']
        os=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
        'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
        size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
        cpu=['octa-core','quad-core']
        back_cm=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
        battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
        return render(request,'webapp/filter_test.html',{'mobiles':mobiles,'colors':colors,
        'os':os,'size':size,'feat':feat,'cpu':cpu,'back_cm':back_cm,'battery':battery})

class filter(TemplateView):
    def get(self,request):
        ''' 
            print("in filter")
            
            print("global",role)
            mobiles=samsung_phone.objects.all()
            m=samsung_phone.objects.all()
            feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')

            colors=['black','white','gold']
            os=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
            'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
            size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
            cpu=['octa-core','quad-core']
            back_cm=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
            battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
            return render(request,'webapp/filter_test.html',{'mobiles':mobiles,'colors':colors,
            'os':os,'size':size,'feat':feat,'cpu':cpu,'back_cm':back_cm,'battery':battery})
        '''
        if request.user.is_authenticated:
            
            colors=['black','white','gold']
            os=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
                'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
            size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
            cpu=['octa-core','quad-core']
            back_cm=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
            battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
            mobilecompany=['samsung','I Phone']
            chip=['Exynos 9810 Octa','Exynos 8895 Octa','Qualcomm Snapdragon 805','Exynos8890Octa','Quad-core (2 x 2.15 GHz Kryo + 2 x 1.6 GHz Kryo)','Exynos 7885 Octa','QualcommMSM8996Snapdragon820','Exynos7420','Exynos 7420 Octa','Exynos 7880 Octa','QualcommMSM8953Snapdragon625','Mediatek MT6757 Helio P20','Exynos 7870 SoC','Exynos 7870','1.4 GHz Quad-Core Cortex-A53','QualcommMSM816Snapdragon410','QualcommMSM8917Snapdragon425','1.2 GHz Quad-core Cortex-A53','Spreadtrum SC9830','MediatekMT6737T','Exynos3475','Spreadtrum SC9830','Spreadtrum','','']
            resolution=['720 x 1280','540 x 960','480 x 800','1440 x 2960','1080 x 2220','1080 x 1920']      
            weight=['163','195','173','174','155','191','157','172','132','0','181','169','179','135','160','170','143','159','146','156','138','131','122','126','153']  
            dimensions=['147.6 x 68.7 x 8.4 mm','162.5 x 74.6 x 8.5 mm','159.5 x 73.4 x 8.1 mm','151.3 x 82.4 x 8.3 mm','148.9 x 68.1 x 8 mm','159.9 x 75.7 x 8.3 mm','150.9 x 72.6 x 7.7 mm','149.2 x 70.6 x 8.4 mm','143.4 x 70.8 x 6.9 mm','142.1 x 70.1 x 7 mm','153.2 x 76.1 x 7.6 mm','156.8 x 77.6 x 7.9 mm','146.1 x 71.4 x 7.9 mm','152.4 x 74.7 x 7.9 mm','146.8 x 75.3 x 8.9 mm','146.8 x 75.3 x 8.9 mm','156.7 x 78.8 x 8.1 mm','135.4 x 66.2 x 7.9 mm']
            if request.user.is_student:
                global  role
                role=1
                feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
                ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
                

            
            elif request.user.is_prof:
                role=2
                feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
                ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
               
                #return redirect('/admin')
            else:
                print("in mobile redirect")
                return redirect('/mobileanl/mobile')  
            
        else:
            print("in else authenticate failed")
            return redirect('/mobileanl/mobile')  


        return render(request,'webapp/filter_test.html',{'colors':colors,
            'os':os,'size':size,'feat':feat,'ft':ft,'cpu':cpu,'back_cm':back_cm,'battery':battery,'mobilecompany':mobilecompany,'chip':chip,'resolution':resolution,'weight':weight,'dimensions':dimensions})
    
    def post(self,request):
        # print("ssss",(request.POST['first_choice_value']))
        # print("ssss",form.cleaned_data['first_choice_value'])
        global sizeofmob
        
        if request.method=="POST":
            first_choice = request.POST['first_choice_value']
            print("fc",first_choice)
            first_choice2 = request.POST['first_choice2_value']
            print("fc2",first_choice2)
            second_choice=request.POST['second_choice_value']
            print("sc",second_choice)
            third_choice=request.POST['third_choice_value']
            print("tc",third_choice)
            fourth_choice=request.POST['fourth_choice_value']
            print("fc",fourth_choice)
            fourth_choice2=request.POST['fourth_choice2_value']
            print("f2c",fourth_choice2)
            fifth_choice=request.POST['fifth_choice_value']
            print("fc",fifth_choice)
            six_choice=request.POST['six_choice_value']
            print("sixc",six_choice)
            seven_choice=request.POST['seven_choice_value']
            print("sevc",seven_choice)
            eight_choice=request.POST['eight_choice_value']
        
            nine_choice=request.POST['nine_choice_value']
            
            ten_choice=request.POST['ten_choice_value']
            
            eleven_choice=request.POST['eleven_choice_value']
            print("ele",eleven_choice)
            twelve_choice=request.POST['twelve_choice_value']
            
            filter = {'Colors' : second_choice,
                 'OS' : third_choice,
                 'Size': {'1':fourth_choice,'2':fourth_choice2},
                 'price':{'1':first_choice,'2':first_choice2},
                 'Cpu'  : fifth_choice,
                 'back_camera':six_choice,
                 'battery' : seven_choice,
                 'Mobile_Companny':eight_choice,
                 'Chip':nine_choice,
                 'Resolution':ten_choice,
                 'Weight':eleven_choice,
                 'Dimensions':twelve_choice
                 }
            print(filter)
            query_array = []
            temparray=[]
            
            for key in filter:
                if (filter[key] != ''):
                    print("key",key)
                    if(key == 'Size' ):
                        temparray=[]
                        for k in filter[key]:
                            if (filter[key][k]!=''):
                                print("in size",filter[key][k])
                                temparray.append(filter[key][k])
                        print(temparray)
                        if  temparray:
                            query_array.append(' '+key +' BETWEEN '+temparray[0]+ ' AND '+ temparray[1] +" " )
                    elif(key == 'price'):
                        temparray=[]
                        for k in filter[key]:
                            if (filter[key][k]!=''):
                                print("in price",filter[key][k])
                                temparray.append(filter[key][k])
                        print(temparray)
                        if  temparray:
                            query_array.append(' '+key +' BETWEEN '+temparray[0]+ ' AND '+ temparray[1]+ " ")
                    else:
                        print("in key else")
                        var=filter[key]
                        query_array.append(' '+key +' LIKE '+"'"+'%%'+var+'%%'+"'")
                
                   
            
            if len(query_array) != 0:
                query = 'SELECT * FROM webapp_samsung_phone WHERE '+ 'AND ' .join(query_array)
                #query= '''SELECT * FROM webapp_samsung_phone where OS like'+"'"+'android v7.1.1 (nougat)'+"'''
                print(query)
                mobiles=samsung_phone.objects.raw(query)
                
                sizeofmob=len(list(mobiles))
                print(sizeofmob)
                
            else:
                query = 'SELECT * FROM webapp_samsung_phone '
                mobiles=samsung_phone.objects.raw(query)
                sizeofmob=len(list(mobiles))
                print(sizeofmob)
            print("ssssa",sizeofmob)
            
          
            
        return render(request,'webapp/mobile.html',{'mobiles':mobiles})


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

class mobile_phone_view(TemplateView):
    template_name='webapp/mobile.html'
    def get(self,request):
        #form=mobile_phone_form(request.POST)
        querry_array=[]
        querry=''
        if not request.user.is_superuser:
            if request.user.is_student:
                
                obj=prunedmobilephones.objects.filter(roles=1)
                for m in obj:
                    querry_array.append(' ' + 'id='+str(m.m_id)+ ' ' )
                    

                querry='SELECT * FROM webapp_samsung_phone WHERE '+ 'or'.join(querry_array)
                print(querry)
                mobiles=samsung_phone.objects.raw(querry)
                return render(request,'webapp/cart.html',{'mobiles':mobiles})
            if request.user.is_prof:
                obj=prunedmobilephones.objects.filter(roles=2)
                print("in here")
                for m in obj:
                    querry_array.append(' ' + 'id='+str(m.m_id)+ ' ' )
                    

                querry='SELECT * FROM webapp_samsung_phone WHERE '+ 'or'.join(querry_array)
                print(querry)
                mobiles=samsung_phone.objects.raw(querry)
                return render(request,'webapp/cart.html',{'mobiles':mobiles})
            
        else:
            mobiles= samsung_phone.objects.all() 
            paginator = Paginator(mobiles,9)
            page = request.GET.get('page')
            mobiles = paginator.get_page(page)
            print(mobiles)
        
            return render(request,self.template_name,{'mobiles':mobiles})
  
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
        singlemob=samsung_phone.objects.filter(id=id1)
        print(singlemob)
        return render(request,'webapp/one_mobile_info.html',{'singlemob':singlemob})
        

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
        
            return render (request, 'webapp/importcsv_form_display.html',{'status':filepath})
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
        print('ikoko',role)
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
        mobiles= samsung_phone.objects.all()
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
            print("file",json_data)
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
                print(dataframe.head())
                expCont.subjData=dataframe
                
                print('subdata head')
                print(expCont.subjData.head())
                # expCont.idField=customid_field
                print('custom id field')
                print(customid_field)
                expCont.setIdField(customid_field)
                print('ExpCont.idField')
                print(expCont.idField)
                expCont.setBatchesTitle(batch_name)
                print('expContsubjdatafield')
                print(expCont.subjData.head())
                pickleExpController(expCont)
                expCont=getExpController(request)


                expCont.subjData=expCont.assigner.splitInBins(batch_num,batch_name,customlabels)
                print('ExpCont_SubjData')
                print(expCont.subjData.head())
                print('Exp assigner df')
                print(expCont.assigner.df.head())
                expCont.saveSubjects()
                dSubBatches=expCont.subjData
                pickleExpController(expCont)

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
            pickledExpCont = pickle.load( open("expCont2.p", "rb") )
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
        print('in else create Exp obj  ')
        expAdminId = request.user.custom_id
        expCont = ExperimentController(a_id=expAdminId)
        print('Exp id',expCont.exp.id)
        request.session['sess_expId'] = expCont.exp.id
        request.session['sess_custExpId'] = expCont.exp.custom_exp_id
        print("SAVED NEW EXPERIMENT TO SESSION---->>>>>>")
    return expCont

def pickleExpController(expCont):
    pickle.dump(expCont, open('expCont2.p','wb'))

def getSavedSubjectDataExpCont(request):
    if request.method == 'POST':
        if request.is_ajax:
            pickleExpCont=pickle.load( open("expCont2.p", "rb") )
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
            print(blocksBreakUp)
        else:
            blocksBreakUp = "Empty"

        data = {    'exp_id':expCont.exp.id,
                    'custom_exp_id':expCont.exp.custom_exp_id,
                    'blocks':blocksBreakUp
        }
        #create to_json dictionary of blocks (by batches, ie. index-wise, then row-wise)
        return JsonResponse(data, safe=False)
def removeSessionObj(request):
    filepath = Path("E:/bias/expCont2.p")
    if filepath:
        os.remove('E:/bias/expCont2.p')
    if request.session['sess_expId']:
        del request.session['sess_expId']


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
                'data':'success'
            }
            
    return HttpResponse()

class createExperiment(TemplateView): 

    
    def get(self,request):       
        # removeSessionObj(request)
        platformfeatobj=platform_feature.objects.all()
        
        try:
            sess_expId = request.session['sess_expId']
            print("sesid",sess_expId)
        except KeyError:
            sess_expId = ""
        try:
            sess_custExpId = request.session['sess_custExpId']
        except KeyError:
            sess_custExpId = "123"
        return render(request,'webapp/crudexperiment/create_experiment.html',
                                        {'platformfeatobj':platformfeatobj,
                                         'sess_expId':sess_expId,
                                         'sess_custExpId':sess_custExpId
                                        }
        )
                                        
                                    
    def post(self,request):
        if request.method=="POST":
            print("====IN CREATEEXP POST METHOD====")
            data = {'data':"data"}

            if request.is_ajax:
                d = request.POST.get('dict')
                #print('d',d)
                postedFLevels = json.loads(d)
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
class datadefined(TemplateView):
    def get(self,request):
        return render(request,'webapp/crudexperiment/datadefined.html')

    def post(self,request):  
      
        return render(request,'webapp/crudexperiment/datadefined.html')     