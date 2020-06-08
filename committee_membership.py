import requests, json, sqlite3, sys

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])

# this function deals with the subcommittees and committees for the later congresses (115 and 116)
# it calls the propublica api for each legislator, gets their committee and subcommittee assignments for their first congress, collects it
# then, it adds their committee membership to the database, assigning it to one of the committees that already exists in the db, as they are fixed
# for the subcommittees, it checks if it exists in the subcommittees table, if it doesn't, it adds an entry to the subcommittees table for the new subcommittee
# after either adding a new subcommittee or getting the id of an existing one, it adds their membership in that subcommittee to the database
def later_congresses():
    cur = conn.cursor()
    cur.execute("select id, bioguide_id, congress from legislators where congress=115 or congress=116")
    legislators = cur.fetchall()
    cur.execute("select name, id from committees")
    db_committees_match = cur.fetchall()
    db_committees_names = []
    for cmte in db_committees_match:
        db_committees_names.append(cmte[0])

    db_committees_ids = []
    for cmte in db_committees_match:
        db_committees_ids.append(cmte[1])

    if legislators != ():
        for legislator in legislators:
            print(legislator[0])
            committees = []
            subcommittees = []
            legislator_id = legislator[0]
            legislator_bioguide_id = legislator[1]
            legislator_congress = legislator[2]                

            url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(legislator_bioguide_id)
            resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()

            result = resp['results'][0]

            for role in result['roles']:
                if role['congress'] == str(legislator_congress):
                    for committee in role['committees']:
                        committees.append({'name': committee['name'], 'code': committee['code']})
                    for subcommittee in role['subcommittees']:
                        subcommittees.append({'name': subcommittee['name'], 'parent_committee_id': subcommittee['parent_committee_id']})
            for cmte in committees:
                parent_id = None

                for i, db_cmte in enumerate(db_committees_names):
                    if db_cmte.split()[0] in cmte['name']:
                        parent_id = db_committees_ids[i]
                        cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, parent_id))
                if cmte['name'] == 'Committee on Administration':
                    parent_id = 11
                    cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, parent_id))
                elif cmte['name'] == "Committee on Veterans' Affairs":
                    parent_id = 19
                    cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, parent_id))

                for subcmte in subcommittees:
                    if subcmte['parent_committee_id'] == cmte['code']:
                        cur.execute("select id from subcommittees where congress={0} and name=\"{1}\" and parent_id={2}".format(legislator_congress, subcmte['name'], parent_id))
                        subcmte_match = cur.fetchall()
                        if len(subcmte_match) > 0:
                            cur.execute("insert into subcommittee_members_v2 (legislator_id, subcommittee_id) values({0}, {1})".format(legislator_id, subcmte_match[0][0]))
                        else:
                            cur.execute("insert into subcommittees (congress, name, parent_id) values({0}, \"{1}\", {2})".format(legislator_congress, subcmte['name'], parent_id))
                            subcommittee_id = cur.lastrowid
                            cur.execute("insert into subcommittee_members_v2 (legislator_id, subcommittee_id) values({0}, {1})".format(legislator_id, subcommittee_id))
    conn.commit()
    conn.close()

# because subcommittee membership is handled by a different script, which pulls the raw data from congressional directory for the specified congress
# this function gets the committee memberships for the legislators in the early congresses (112, 113, and 114) from propublica's congress api
# then adds those memberships to the database
# veteran's affairs and house administration are special cases - veterans because it has a weird character and admin because the first word "house" doesn't help in the filtering process
def earlier_congresses():
    cur = conn.cursor()
    cur.execute("select id, bioguide_id, congress from legislators where congress=112 or congress=113 or congress=114")
    legislators = cur.fetchall()
    cur.execute("select name, id from committees")
    db_committees_match = cur.fetchall()
    db_committees_names = []
    for cmte in db_committees_match:
        db_committees_names.append(cmte[0])

    db_committees_ids = []
    for cmte in db_committees_match:
        db_committees_ids.append(cmte[1])    

    if legislators != ():
        for legislator in legislators:
            print(legislator[0])
            committees = []
            legislator_id = legislator[0]
            legislator_bioguide_id = legislator[1]
            legislator_congress = legislator[2]                

            url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(legislator_bioguide_id)
            resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()

            result = resp['results'][0]

            for role in result['roles']:
                if role['congress'] == str(legislator_congress):
                    for committee in role['committees']:
                        committees.append(committee['name'])

            for cmte in committees:
                for i, db_cmte in enumerate(db_committees_names):
                    if db_cmte.split()[0] in cmte: # if the first word of the committee entry from the database is in the committee name from the api
                        cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, db_committees_ids[i]))
                if cmte == 'Committee on Administration':
                    cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, 11))
                elif cmte == "Committee on Veterans' Affairs":
                    cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, 19))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    globals()[sys.argv[1]]() # run function from command line