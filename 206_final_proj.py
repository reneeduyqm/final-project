# from types import NoneType
from re import S
# from turtle import color
import requests
import time
import json
import sqlite3
import os
import matplotlib.pyplot as plt
import numpy as np
import csv


def CreateDB(db_name):
    name = f'{db_name}.db'
    conn = sqlite3.connect(name)
    cur = conn.cursor()
    return cur, conn 
# def Drop_table(cur,conn):
#     cur.execute('DROP TABLE IF EXISTS Air_Pollution_Death')
#     cur.execute('DROP TABLE IF EXISTS COVID_TEST')
#     conn.commit()
    
def Air_Pollution_Death(cur,conn):
    data = requests.get('https://ghoapi.azureedge.net/api/AIR_41').json()
    with open('air_pollution_death.json','w') as f:
        json.dump(data,f,indent=4)
    cur.execute('CREATE TABLE IF NOT EXISTS Air_pollution_Death (ID NUMBER PRIMARY KEY, Country TEXT, Cause_ID TEXT, Gender TEXT, Number_of_Death FLOAT)')
    cur.execute('SELECT MAX(ID) FROM Air_pollution_Death')
    # temp = type(cur.fetchone()[0])
    # print(temp)
    temp = cur.fetchone()[0]
    if not temp:
        index = 0
    else:
        # index = int(cur.fetchone()[0])
        index = int(temp)
    # print(index)
    for i in range(len(data['value']))[index:]:
        country = data['value'][i]['SpatialDim']
        cid = data['value'][i]['Dim2']
        g = data['value'][i]['Dim1']
        num = data['value'][i]['NumericValue']
        # print(i)
        cur.execute('INSERT INTO Air_Pollution_Death (ID, Country, Cause_ID, Gender, Number_of_Death) VALUES (?,?,?,?,?)',
            (i+1, country, cid, g, num)) 
        index += 1
        if(index % 25 == 0):
            break
    conn.commit()

def Air_Pollution_Category(cur,conn):
    cur.execute('CREATE TABLE IF NOT EXISTS Air_Pollution_Category (Category_ID TEXT PRIMARY KEY, Catagory_Type TEXT, Category_Name TEXT)')
    conn.commit()
    data = [{"c":"ENVCAUSE039","type":"ENVCAUSE","name":"Lower Respiratory Infections"},
            {"c":"ENVCAUSE068","type":"ENVCAUSE","name":"Trachea, Bronchus, Lung Cancers"},
            {"c":"ENVCAUSE113","type":"ENVCAUSE","name":"Ischaemic Heart Disease"},
            {"c":"ENVCAUSE114","type":"ENVCAUSE","name":"Stroke"},
            {"c":"ENVCAUSE118","type":"ENVCAUSE","name":"Chronic Obstructive Pulmonary Disease"}
        ]
    for i in range(len(data)):
        c = data[i]['c']
        t = data[i]['type']
        n = data[i]['name']
        cur.execute('INSERT INTO Air_Pollution_Category (Category_ID, Catagory_Type, Category_Name) VALUES (?,?,?)',(c,t,n))
        conn.commit()
        
def Air_Pollution_cate_Pie_Chart (cur,conn):
    cur.execute('SELECT C.Category_Name, COUNT(*) FROM Air_Pollution_Death d JOIN Air_Pollution_Category c on d.Cause_ID = c.Category_ID GROUP BY c.Category_Name')
    conn.commit()
    total = 0
    dict = {}
    for t in cur.fetchall():
        dict[t[0]] = t[1]
        total += t[1]
    labels = []
    value = []
    for keys in dict.keys():
        labels.append(keys)
        value.append(int((dict[keys]/total)*100))
    
    explode = (0, 0.1, 0, 0) 
    fig1, ax1 = plt.subplots(figsize =(6.5,5))
    plt.rcParams.update({'font.size': 7})
    ax1.pie(value, explode=explode, labels=labels, autopct='%2.1f%%',
            shadow=True, startangle=90)
    ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.title('Air Pollution Death Category', bbox={'facecolor':'0.8', 'pad':5})
    plt.savefig('Air Pollution Death Category.png')

    with open('Air Pollution Death Category.csv','w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(labels)
        csv_writer.writerow(value)


def Air_Pollution_Gender_bar_chart(cur,conn):
    cur.execute('SELECT d.Country, c.Category_Name,d.Gender,COUNT(*) FROM Air_Pollution_Death d JOIN Air_Pollution_Category c on d.Cause_ID = c.Category_ID GROUP BY d.Country,d.Gender Order by d.Country,c.Category_Name,COUNT(*)')
    conn.commit()
    # print(cur.fetchall())
    temp = []
    values = []
    for t in cur.fetchall():
        tup = (t[0],t[1],t[2])
        temp.append(tup)
        values.append(t[3])
    y_pos = [i for i, _ in enumerate(temp)]
    fig1, ax1 = plt.subplots(figsize =(23,8))
    plt.rcParams.update({'font.size': 7})
    plt.barh(y_pos,values)
    plt.ylabel('causes, gender, country')
    plt.xlabel('Number of Death')
    plt.title('Death of Air_Pollution_Death with different Cause in Countries within Different Gender')
    plt.yticks(y_pos,temp)
    plt.savefig('Air_Pollution_Gender_bar_chart.png')

def COVID_API(cur,conn):
# def COVID_API():
    cur.execute('CREATE TABLE IF NOT EXISTS COVID_TEST (Date NUMBER PRIMARY KEY, Positive NUMBER, Negative NUMBER, Currently_Hospitalized NUMBER,Cumulative_Hospitalized NUMBER)')
    cur.execute('SELECT MAX(Date) FROM COVID_TEST')
    temp = cur.fetchone()[0]
    # print(str(temp))
    if not temp:
        mon = 3
        day = 1
    else:
        mon = int(str(temp)[4]+ str(temp)[5])
        day = int (str(temp)[6]+str(temp)[7])+1
    if(day == 30):
        day = 1
        mon = mon + 1
    # sys.exit()
    count = 0
    flag = False

    for m in range(13)[mon:]: 
        if count!= 0:
            day = 1
        for d in range(30)[day:]:   
            req_date = f'2020'
            if( m < 10):
                req_date +=f'0{m}'
            else:
                req_date += f'{m}'
            if(d < 10):
                req_date +=f'0{d}'
            else:
                req_date +=f'{d}'
            
            req = f'https://api.covidtracking.com/v1/us/{req_date}.json'
            count += 1
            # print(req)
            data = requests.get(req).json()
            # print(data)
            # print(data)

            date = data['date']
            num_pos = data['positive']
            num_neg = data['negative']
            cur_hos = data['hospitalizedCurrently']
            accu_hos = data['hospitalizedCumulative']
            cur.execute('INSERT INTO COVID_TEST (Date , Positive , Negative ,Currently_Hospitalized, Cumulative_Hospitalized) VALUES (?,?,?,?,?)',
                (date, num_pos, num_neg,cur_hos, accu_hos))
            conn.commit()
            # print(count)
            if(count == 25):
                flag = True
                break
        if flag == True:
            break
    # conn.`commit()

def COIVD_API_stacked_Area_Chart(cur,conn):
    cur.execute('SELECT Date, Positive, Negative FROM COVID_TEST LIMIT 50')
    conn.commit()
    date = []
    lst_pos = []
    lst_neg = []
    for t in cur.fetchall():
        # print(t)
        
        date.append(str(t[0])[4:])
        lst_pos.append(t[1])

        lst_neg.append(t[2])

    x=date
    y1=lst_pos
    y2=lst_neg
    # y3=[2,8,5,10,6]

    # Basic stacked area chart.
    
    fig = plt.figure(figsize=(20, 2))
    ax = fig.add_subplot(111)
    # ax.plot()
    ax.stackplot(x,y1, y2,  labels=['Positive','Negative'])
    ax.legend(loc='upper left')
    plt.tight_layout()
    plt.savefig('test_pos.png')

    

    

def main():
    db_name = '206_final'
    cur, conn = CreateDB(db_name)

    COVID_API(cur, conn)
    Air_Pollution_Death(cur,conn)

    # check if Air_Pollution Category table already in the database
    cur.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='Air_Pollution_Category' ''')
    if cur.fetchone()[0] == 0:
        Air_Pollution_Category(cur, conn)
    conn.commit()
    
    Air_Pollution_cate_Pie_Chart(cur, conn)
    Air_Pollution_Gender_bar_chart(cur,conn)
    cur.execute('SELECT COUNT(*) FROM COVID_TEST')
    conn.commit()
    limit = cur.fetchone()[0]
    # print(cur.fetchone()[0])s
    if limit > 50:
        print('area chart')
        COIVD_API_stacked_Area_Chart(cur,conn)

    # cur.execute('DROP TABLE IF EXISTS Air_Pollution_Death')
    # conn.commit()
    
    # COVID_API()
if __name__ == '__main__':
    main()