# this file got all the subcommittees and committees for the legislators in the 115th and 116th congress, because that is where the propublica data was available
# however, it is not needed anymore as the methods have changed
import requests, json, sqlite3

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

cur.execute("select id, bioguide_id, congress from legislators where congress=115 or congress=116")
legislators = cur.fetchall()
count = 0

if legislators != ():
    for legislator in legislators:
        count += 1
        legislator_id = legislator[0]
        legislator_bioguide_id = legislator[1]
        legislator_congress = legislator[2]

        committees = []
        subcommittees = []

        url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(legislator_bioguide_id)
        resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()

        result = resp['results'][0]

        for role in result['roles']:
            if role['congress'] == str(legislator_congress):
                for committee in role['committees']:
                    committees.append({'name': committee['name'], 'code': committee['code']})
                for subcommittee in role['subcommittees']:
                    subcommittees.append({'name': subcommittee['name'], 'code': subcommittee['code'], 'parent': subcommittee['parent_committee_id']})

                for committee in committees:
                    cur.execute("insert into committee_members (legislator_id, name, code) values ({0}, \"{1}\", '{2}')".format(legislator_id, committee['name'], committee['code']))
                    committee['id'] = cur.lastrowid
                
                for subcommittee in subcommittees:
                    parent_code = subcommittee['parent']
                    parent_id = ''

                    for committee in committees:
                        if committee['code'] == parent_code:
                            parent_id = committee['id']

                    if parent_id != '':
                        cur.execute("insert into subcommittee_members (legislator_id, name, code, parent_id) values ({0}, \"{1}\", '{2}', {3})".format(legislator_id, subcommittee['name'], subcommittee['code'], parent_id))

conn.commit()
conn.close()
