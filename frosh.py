import yaml, requests, json, sqlite3

with open('config.json') as file:
    config = json.load(file)

#
#
#
#
# DO NOT RUN THIS CODE WITHOUT CHECKING alt_full_names
#
#
#
#
#
conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

start_dates_congress = {
    '2011-01-05': 112,
    '2013-01-03': 113,
    '2015-01-06': 114,
    '2017-01-03': 115,
    '2019-01-03': 116
}

start_dates = list(start_dates_congress) # list of keys

with open('data/legislators.yaml') as file:
    legislators = yaml.full_load(file)
    print('YAML Loaded.')

count = 0
for legislator in legislators:
    first_term = legislator['terms'][0]
    start_date = first_term['start'] # first sworn in date in congress
    rep_type = first_term['type']

    if start_date in start_dates and rep_type == 'rep':
        count += 1

        congress = start_dates_congress[start_date]
        election_year = int(start_date[:4]) - 1 # first 4 characters i.e. 2015 - 1 = 2014 election year
        state = first_term['state']
        party = first_term['party']
        district = first_term['district']
        first_name = legislator['name']['first']
        last_name = legislator['name']['last']
        full_name = legislator['name']['official_full']
        bioguide_id = legislator['id']['bioguide']
        crp_id = legislator['id']['opensecrets']
        
        # This array is necessary because for some candidates, the dataset returns > 1 fec id, but the second one always seems to be invalid
        cand_fec_arr = []
        for cand_fec in legislator['id']['fec']:
            if cand_fec[0] == 'H':
                cand_fec_arr.append(cand_fec)

        candidate_fec_id = cand_fec_arr[0]
        committee_fec_id = ''
        url = 'https://api.open.fec.gov/v1/candidate/{0}/committees/history?api_key={1}'.format(candidate_fec_id, config['DATA_GOV_API_KEY'])
        resp = requests.get(url).json()

        for result in resp['results']:
            if result['designation'] == 'P' and result['committee_type'] == 'H' and 2010 in result['cycles']:
                committee_fec_id = result['committee_id']
        # before running this....remember alt_full_names
        if committee_fec_id == '':
            print(full_name, candidate_fec_id)
        print(count, congress, election_year, state, party, district, full_name, bioguide_id, crp_id, candidate_fec_id, committee_fec_id)
        cur.execute("insert into legislators (first_name, last_name, full_name, election_year, congress, state, party, district, bioguide_id, crp_id, candidate_fec_id, committee_fec_id) values('{0}', '{1}', '{2}', {3}, {4}, '{5}', '{6}', {7}, '{8}', '{9}', '{10}', '{11}')"
            .format(first_name, last_name, full_name, election_year, congress, state, party, district, bioguide_id, crp_id, candidate_fec_id, committee_fec_id))

conn.commit()
conn.close()