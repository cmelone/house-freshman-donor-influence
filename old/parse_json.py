import json
import pandas
df = pandas.read_csv('candidates.csv')
congresses = [112, 113, 114, 115, 116]
df['BIO_ID'] = ''

for congress in congresses:
    with open('{0}.json'.format(congress)) as file:
        data = json.load(file)
    for row in df.itertuples():
        last_name = row.Freshman.split()[-1]
        first_name = row.Freshman.split()[0]
        state = row.State
        district = row.District
        if row.BIO_ID == '':
            for m in data['results'][0]['members']:
                #if district == 0:
                #    at_large = True
                #    district = 'At-Large'
                #else:
                #    at_large = False
                if (m['state'] == state) and (m['first_name'] == first_name) and (m['last_name'] == last_name):
                    print(m['id'])
                    df.at[row.Index, 'BIO_ID'] = m['id']
df.to_csv('candidates_id.csv', encoding='utf-8', index=False)
