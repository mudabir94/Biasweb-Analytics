# import datetime
# import mysql.connector

# def populate_Table(tabname,csvpath):
#     cnx = mysql.connector.connect(user='root',password="Opensesame1",host='127.0.0.1', database='django_biasweb6')
#     cursor = cnx.cursor()
#     tablename=tabname
#     csvfilepath=csvpath
#     #csvfile='C://Users//ITU User//Desktop//webapp_table_data_csv_sept//webapp_samsung_phone_for_djangoapp.csv'
#     #tablename='django_biasweb6.webapp_phone'
#     query =("""load data local infile """+"'"+csvfilepath+"'"+""" into table """+tablename+"""
#     fields terminated by ","
#     enclosed by '"'
#     lines terminated by '\n'
#     IGNORE 1 LINES
#     (id, Mobile_Companny,Mobile_Name,Whats_new,OS,Dimensions,Weight,Colors,Cpu,
#     Chip,Gpu,Size,Resolution,rating,back_camera,battery,imagepath1,imagepath2,
#     price_in_pkr,price_in_usd)""")
#     print(query)

#     cursor.execute(query)
#     cnx.commit()
#     cursor.close()
#     cnx.close()
    
#     return ('ok')