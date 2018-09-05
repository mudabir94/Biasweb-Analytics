from django.conf.urls import url, include
from django.urls import path
from . import views

urlpatterns = [
    url(r'^test/',views.test, name='test'),                ## 
    url(r'^ind/',views.ind, name='ind'),                   ##  These urls doesn't have templates. These functions are
    url(r'^on/',views.on, name='on'),                      ##  called  through ajax. They are either used to retrieve           
    url(r'^globalFunc/',views.globalFunc,name='gf'),       ##  data from model and render the data to some other template.
                                                           ##  
    
    
    
    url(r'^admin_setup/',views.adminSetup, name='admin_setup'),
    url(r'^$', views.signUp, name='signup'), 
    
    url(r'^blog/', views.blogview.as_view(), name='blog'), 
    url(r'^mobile/',views.mobile_phone_view.as_view(),name='mobileview'),
    path('mobile_info/<int:id>',views.mobile_phone_view.one_mobile_func, name='mobileinfo'),
    url(r'^filter/',views.filter.as_view(), name='filter'),
    url(r'^showfilter/',views.showFilter.as_view(), name='showfilter'),
    
    url(r'^cart/',views.cart, name='cart'),
    url(r'^showmob/',views.showMob, name='sm'),
    url(r'^showScore/',views.showScore, name='showscore'),


   
]
