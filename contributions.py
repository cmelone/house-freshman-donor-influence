import sqlite3, sys, json
import pandas as pd

with open('config.json') as file:
    config = json.load(file)

df = pd.read_csv('data/dime_candidates.csv')

conn = sqlite3.connect(config['SQLITE_PATH'])
df1 = pd.DataFrame()

# for row in df.itertuples():
#     cycle = row.cycle
#     bonica_rid = row._9 # 9th column, pandas doesn't recognize periods in column names, refer to codebook for indices
#     #print(row.name, row.winn_60er)
#     print(bonica_rid, row.name, cycle)

df1 = df1.append(pd.read_sql("select * from contributions_{0} where \"bonica.rid\"='{1}'".format(2018, 'cand142805'), conn))

df1.to_csv('wpw.csv', encoding='utf-8', index=False)