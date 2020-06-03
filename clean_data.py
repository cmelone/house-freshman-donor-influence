import pandas, requests, sys, json

with open('config.json') as file:
    config = json.load(file)

# https://gist.github.com/rogerallen/1583593
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

abbrev_us_state = dict(map(reversed, us_state_abbrev.items()))

def states_parties():
    df = pandas.read_csv('data/candidates_dirty.csv', dtype={'Party': str, 'District': 'Int64'})

    for row in df.itertuples():
        # Change Parties
        if row.Freshman[-3:] == '(R)':
            df.at[row.Index, 'Party'] = 'R'
        elif row.Freshman[-3:] == '(D)':
            df.at[row.Index, 'Party'] = 'D'
        elif row.Freshman[-3:] == '(I)':
            df.at[row.Index, 'Party'] = 'I'
        df.at[row.Index, 'Freshman'] = row.Freshman[:-4]

        # Change Districts
        state_split = row.State.split()
        district_split = state_split[-1] # last element in array, aka the district
        if district_split == 'AL':
            district_split = 0
        else:
            district_split = int(district_split)

        df.at[row.Index, 'District'] = district_split

        # Change States
        wo_district = state_split[:-1]
        if len(wo_district) == 2:
            state = wo_district[0] + ' ' + wo_district[1]
        else:
            state = wo_district[0] # list to string

        # replace state with abbreviation
        df.at[row.Index, 'State'] = us_state_abbrev[state]

    df.to_csv('data/candidates.csv', encoding='utf-8', index=False)

def bio_id_match():
    # this function is not perfect, so it will not be able to fill in all the IDs
    # data/candidates_id_complete.csv has all the missing IDs filled in manually
    df = pandas.read_csv('data/candidates.csv')
    congresses = [112, 113, 114, 115, 116]
    df['BIO_ID'] = ''

    for congress in congresses:
        with open('ex_data/{0}.json'.format(congress)) as file:
            data = json.load(file)
        for row in df.itertuples():
            last_name = row.Freshman.split()[-1]
            first_name = row.Freshman.split()[0]
            state = row.State
            district = row.District
            if row.BIO_ID == '':
                for m in data['results'][0]['members']:
                    if (m['state'] == state) and (m['first_name'] == first_name) and (m['last_name'] == last_name):
                        df.at[row.Index, 'BIO_ID'] = m['id']
    df.to_csv('data/candidates_id_missing.csv', encoding='utf-8', index=False)

def fec_id_match():
    df = pandas.read_csv('data/candidates_nodups.csv')
    df['FEC_ID'] = ''
    for row in df.itertuples():
        name = row.Freshman
        url = 'https://api.open.fec.gov/v1/names/candidates?api_key={0}&q={1}'.format(config['DATA_GOV_API_KEY'], name)
        resp = requests.get(url).json()

        for r in resp['results']:
            if r['office_sought'] == 'H':
                df.at[row.Index, 'FEC_ID'] = r['id']
    
    df.to_csv('data/candidates_fec.csv', encoding='utf-8', index=False)
# def crp_id_match():
#     df = pandas.read_csv('data/candidates_nodups.csv')
#     congresses = [112, 113, 114, 115, 116]
#     df['first'] = ''
#     df['last'] = ''
#     for congress in congresses:
#         with open('ex_data/{0}.json'.format(congress)) as file:
#             data = json.load(file)
#         for row in df.itertuples():
#             BIO_ID = row.BIO_ID
#             if row.last == '':
#                 for m in data['results'][0]['members']:
#                     if BIO_ID == m['id']:
#                         df.at[row.Index, 'last'] = m['last_name']
#             if row.first == '':
#                 for m in data['results'][0]['members']:
#                     if BIO_ID == m['id']:
#                         df.at[row.Index, 'first'] = m['first_name']
#                         # if m['crp_id'] == None:
#                         #     df.at[row.Index, 'CRP_ID'] = 'replace'
#                         # else:
#                         #     df.at[row.Index, 'CRP_ID'] = m['crp_id']                
#     df.to_csv('data/candidates_name.csv', encoding='utf-8', index=False)
    
def find_dups():
    # this function will only output the duplicate ids, you will have to go in manually to remove the rows from the csv..do this programmatically?
    df = pandas.read_csv('data/candidates_id_complete.csv', usecols=['BIO_ID'])

    for row in df.itertuples():
        url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(row.BIO_ID)
        resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()
        last_role = resp['results'][0]['roles'][-1]
        if int(last_role['congress']) < 112:
            print(row.BIO_ID)

if __name__ == '__main__':
    globals()[sys.argv[1]]() # run function from command line