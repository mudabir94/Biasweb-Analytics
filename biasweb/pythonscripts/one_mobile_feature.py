# -*- coding: utf-8 -*-
"""
Created on Wed Mar 14 05:54:54 2018

@author: Mudabir Ahmad
"""

from datetime import date, datetime, timedelta
import mysql.connector

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
count=0
list_o={}
temp_list={}
index_list=[]
k_list=[]
v_list=[]
page1=requests.get("https://www.whatmobile.com.pk/Qmobile_N230")
soup1 = BeautifulSoup(page1.text,"lxml")


for table_row in soup1.select(" table.specs tr"):
   
    
    cell=table_row.findAll('th')
    cells = table_row.findAll('td')
    print(" ")
    if len(cells) >0 and len(cell) >0:
        if(len(cell)==2):
            index_list.append(cell[1].text.strip())
            list_o[cell[1].text.strip()]=cells[0].text.strip()
            #for item in cell:
                #index_list.append(item.text.strip()
                #list.append( cells[0].text.strip())
        else:
            index_list.append(cell[0].text.strip())
            list_o[cell[0].text.strip()]=cells[0].text.strip()
    		  #count=count+1
            #if count==41:
                #break
#print(list_o)
if list_o=={}:
    for table_row in soup1.select(" div.Heading1 tr"):
        cell=table_row.findAll('th')
        cells = table_row.findAll('td')
        print(" ")
        if len(cells) >0 and len(cell) >0:
            if(len(cell)==2):
                index_list.append(cell[1].text.strip())
                list_o[cell[1].text.strip()]=cells[0].text.strip()
                #for item in cell:
                    #index_list.append(item.text.strip()
                    #list.append( cells[0].text.strip())
            else:
                index_list.append(cell[0].text.strip())
                list_o[cell[0].text.strip()]=cells[0].text.strip()
        		  #count=count+1
                #if count==41:
                    #break
    print("empty")
#print(list_o)

   

if 'Whats_New' in list_o:
    print ("blah")
else:
    soup = BeautifulSoup(page1.content, 'html.parser')
  #  description = soup.find('span', attrs={'itemprop': 'description'})
    #description  =description.text.strip() 
          
   # temp_list['Whats_New']=description
 
    
   # dest = dict(list_o)  
    #list_o.update(temp_list)
   # print(list_o)
   # print("else")

for key,value in list_o.items() :
    k=key 
    if k !='Price in Pakistan':  
        if k!='in Rs.':
            if k!='in USD':
                if k:                                                                       
                    
                        if('-' in k)==True:
                            k=k.replace("-","_")
                            
                        if ('\n' in k)==True:  
                            # k = " ".join(re.split("\s+", k, flags=re.UNICODE))
                            k=k.translate( { ord(k):None for k in ' \n\t\r' } )
                            
                            print("enter")
                        if (' ' in k)== True:
                            k=k.replace(" ","_")
                       # if  not k:
                       #     k=k.replace("","Cont")
                        v=value
                        v=value.replace('"',"'")
                        v=value.replace("'"," ")
                        v=value.replace("\xa0", "")
                        k_list.append(k)
                        v_list.append(v)

string=str(tuple(v_list))
print(k_list)
print("")
print(string)

col=', '.join(k_list)

'''
cnx = mysql.connector.connect(user='root', database='mobile_phones')
cursor = cnx.cursor()
add = ("INSERT INTO mobile_features"
               "("+col+")"
               "VALUES "+string)
print(add)

cursor.execute(add)

cnx.commit()
cursor.close()
cnx.close()
'''