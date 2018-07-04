from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import TemplateView
from .forms import blogForm,SignUpForm,mobile_phone_form,filterform,sort_filter_form
from .models import blog,mobile_phone,phone,samsung_phone,sort_feature,userscoreRecord
from django.http import HttpResponse
from django.contrib.auth import login as auth_login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.db import connection
from django.db.models import Q
import json
from django.utils import timezone

role=1   #global variable used in adminsetup and globalFunc function. 
mobiles=samsung_phone.objects.raw('SELECT * FROM webapp_samsung_phone WHERE id=1 or id=2') # making mobiles object global.
sizeofmob=0 # global variable assigned in filter class.
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
                print(featname,featpriority,mobileid,userid,elementid,columnId)
                # p = userscoreRecord(column_id=columnId,element_id=elementid,feat_priority=featpriority,feat_name=featname,mobile_id=mobileid,user_id=userid,date_created=timezone.now(), date_modified=timezone.now())
                # print("p",p)
                # p.save()

    
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
                    
            if request.user.is_student:
                global  role
                role=1
                feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
                ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
                colors=['black','white','gold']
                os=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
                    'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
                size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
                cpu=['octa-core','quad-core']
                back_cm=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
                battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']

            
            elif request.user.is_prof:
                role=2
                feat=sort_feature.objects.filter(~Q(sh_hd = 0),roles=role).order_by('position')
                ft=sort_feature.objects.filter(Q(sh_hd = 0),roles=role).order_by('position')
                colors=['black','white','gold']
                os=['android v8.0 oreo','android v7.1.1 (nougat)','android v4.4 (kitkat)','android v6.0 (marshmallow)',
                    'android v5.0.2 (lollipop)','android v5.1 (lollipop)','android v4.3 (jelly bean)']
                size=['0','1','3','4','4.1','4.2','4.3','4.4','4.5','4.6','4.7','4.8','4.9','5','5.1','5.2','5.3','5.4','5.5','5.6','5.7','5.8','5.9','6','6.1','6.2','6.3','6.4','6.5','6.6','6.7','6.8','6.9','7']
                cpu=['octa-core','quad-core']
                back_cm=['16 MP','13 MP','8 MP','5.0 MP','3.7 MP','2 MP','1.9 MP','VGA']
                battery=['3600 mAh','3300 mAh','3000 mAh','2600 mAh','2400 mAh','2350']
                #return redirect('/admin')
            else:
                print("in mobile redirect")
                return redirect('/mobileanl/mobile')  
            
        else:
            print("in else authenticate failed")
            return redirect('/mobileanl/mobile')  


        return render(request,'webapp/filter_test.html',{'colors':colors,
            'os':os,'size':size,'feat':feat,'ft':ft,'cpu':cpu,'back_cm':back_cm,'battery':battery})
    
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

            filter = {'Colors' : second_choice,
                 'OS' : third_choice,
                 'Size': {'1':fourth_choice,'2':fourth_choice2},
                 'price':{'1':first_choice,'2':first_choice2},
                 'Cpu'  : fifth_choice,
                 'battery' : seven_choice}
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
            return render(request,'webapp/mobile.html',{'form':form})

    def one_mobile_func(request,id):
        id1=id
        print(id1)
        singlemob=samsung_phone.objects.filter(id=id1)
        print(singlemob)
        return render(request,'webapp/one_mobile_info.html',{'singlemob':singlemob})

    

        
