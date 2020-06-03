import sqlite3, sys, json
import pandas as pd

with open('config.json') as file:
    config = json.load(file)

df = pd.read_csv('data/candidates_fec.csv')

conn = sqlite3.connect(config['SQLITE_PATH'])
df1 = pd.DataFrame()

for row in df.itertuples():
    seat = 'federal:house'
    cycle = row.Cycle
    FEC_ID = row.FEC_ID
    df1 = df1.append(pd.read_sql("select * from recipients where cycle='{0}' and seat='federal:house' and \"Cand.ID\"='{1}'".format(cycle, FEC_ID), conn))


conn.close()

df1.to_csv('data/dime_candidates.csv', encoding='utf-8', index=False)