import sqlite3, sys, json, requests
import pandas as pd

with open('config.json') as file:
    config = json.load(file)

df = pd.read_csv('data/candidates_fec.csv')

conn = sqlite3.connect('/Volumes/Misc/Money in Politics/crp/crp.db')

df['FEC_CMTE_ID'] = ''

for row in df.itertuples():
    FEC_ID = row.FEC_ID

    url = 'https://api.open.fec.gov/v1/candidate/{0}/committees/history?api_key={1}'.format(FEC_ID, config['DATA_GOV_API_KEY'])
    resp = requests.get(url).json()

    for record in resp['results']:
        if record['designation'] == 'P' and record['committee_type'] == 'H':
            df.at[row.Index, 'FEC_CMTE_ID'] = record['committee_id']
        else:
            print(FEC_ID)

df.to_csv('data/candidates_fec_cmte.csv', encoding='utf-8', index=False)