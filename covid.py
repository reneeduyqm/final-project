from bs4 import BeautifulSoup
import sqlite3
import requests
import matplotlib.pyplot as plt
import os
import numpy as np


def CreateDB(db_name):
    name = f'{db_name}'
    conn = sqlite3.connect(name)
    cur = conn.cursor()
    return cur, conn 

def create_covid_table(cur, conn):
    cur.execute('CREATE TABLE IF NOT EXISTS covid (Country TEXT PRIMARY KEY, Cases INTEGER, Deaths INTEGER, Region TEXT )')
    conn.commit()

def add_covid(cur, conn):

    data = requests.get('https://www.worldometers.info/coronavirus/countries-where-coronavirus-has-spread')
    soup = BeautifulSoup(data.content, 'html.parser')
    matches = soup.find_all('tbody')
    for match in matches:
        data = match.find_all('tr')

    for item in data:
        temp = item.find_all('td')
        country = temp[0].text
        case_b = temp[1].text
        case = int(case_b.replace(',', ''))
        death_b = temp[2].text
        death = int(death_b.replace(',', ''))
        region = temp[3].text
        cur.execute(
            """
            INSERT OR IGNORE INTO covid (Country, Cases, Deaths, Region)
            VALUES (?, ?, ?, ?)
            """,
            (country, case, death, region)
        )
    conn.commit()

def covid_bar_chart(cur,conn):
    cur.execute('SELECT Deaths, Country FROM covid LIMIT 10')
    conn.commit()

    temp = []
    values = []
    dict = {}
    for t in cur.fetchall():
        temp.append(t[0])
        values.append(t[1])
        dict[t[0]] = t[1]

    objects = tuple(temp)
    y_pos = np.arange(len(objects))
    fig1, ax1 = plt.subplots(figsize =(23,8))

    plt.bar(y_pos,values,align='center',alpha=1)
    plt.xticks(y_pos,objects)
    
    plt.xlabel('Country')
    plt.ylabel('Number of Deaths')
    plt.title('Number of Deaths by Country')
    plt.savefig('Number_Deaths_by_Country_bar_chart.png')

    plt.show()
    return dict



def main():
    cur, conn = CreateDB("covid.db")
    create_covid_table(cur,conn)
    add_covid(cur, conn)
    covid_bar_chart(cur, conn)

if __name__ == "__main__":
    main()




