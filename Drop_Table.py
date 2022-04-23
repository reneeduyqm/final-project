import sqlite3

conn = sqlite3.connect('206_final.db')
cur = conn.cursor()

cur.execute('DROP TABLE IF EXISTS Air_Pollution_Death')
cur.execute('DROP TABLE IF EXISTS COVID_TEST')
cur.execute('DROP TABLE IF EXISTS Air_Pollution_Category')
conn.commit()