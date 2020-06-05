import requests, pandas

df = pandas.read_csv('candidates_id.csv', usecols=['BIO_ID'])

for row in df.itertuples():
    url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(row.BIO_ID)
    resp = requests.get(url, headers={'X-API-Key': ''}).json()
    last_role = resp['results'][0]['roles'][-1]
    if int(last_role['congress']) < 112:
        print(row.BIO_ID)

