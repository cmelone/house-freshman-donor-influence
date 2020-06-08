import requests, json, sqlite3

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])
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
                #print(role['subcommittees'])
                for committee in role['committees']:
                    committees.append({'name': committee['name'], 'code': committee['code']})
                for subcommittee in role['subcommittees']:
                    subcommittees.append({'name': subcommittee['name'], 'parent_committee_id': subcommittee['parent_committee_id']})
        #print(subcommittees)
        for cmte in committees:
            parent_id = None

            for i, db_cmte in enumerate(db_committees_names):
                if db_cmte.split()[0] in cmte['name']:
                    parent_id = db_committees_ids[i]
                    #print(db_cmte.split()[0], cmte['name'])
                    cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, parent_id))
            if cmte['name'] == 'Committee on Administration':
                parent_id = 11
                #print('admin')
                cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, parent_id))
            elif cmte['name'] == "Committee on Veterans' Affairs":
                #print('veteran')
                parent_id = 19
                cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, parent_id))

            #print('hi')
            # get the subcommittee id 
            for subcmte in subcommittees:
                if subcmte['parent_committee_id'] == cmte['code']:
                    cur.execute("select id from subcommittees where congress={0} and name=\"{1}\" and parent_id={2}".format(legislator_congress, subcmte['name'], parent_id))
                    subcmte_match = cur.fetchall()
                    if len(subcmte_match) > 0:
                        print(1)
                        cur.execute("insert into subcommittee_members_v2 (legislator_id, subcommittee_id) values({0}, {1})".format(legislator_id, subcmte_match[0][0]))
                    else:
                        #print("insert into subcommittees (congress, name, parent_id) values({0}, \"{1}\", {2})".format(legislator_congress, subcmte['name'], parent_id))
                        cur.execute("insert into subcommittees (congress, name, parent_id) values({0}, \"{1}\", {2})".format(legislator_congress, subcmte['name'], parent_id))
                        subcommittee_id = cur.lastrowid
                        cur.execute("insert into subcommittee_members_v2 (legislator_id, subcommittee_id) values({0}, {1})".format(legislator_id, subcommittee_id))
                    #print(subcmte['name'], cmte['name'])
                #JSON request schema is not the way in which youre writing it-need to track subcommittee by committee id 


# if legislators != ():
#     for legislator in legislators:
#         print(legislator[0])
#         committees = []
#         legislator_id = legislator[0]
#         legislator_bioguide_id = legislator[1]
#         legislator_congress = legislator[2]                

#         url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(legislator_bioguide_id)
#         resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()

#         result = resp['results'][0]

#         for role in result['roles']:
#             if role['congress'] == str(legislator_congress):
#                 for committee in role['committees']:
#                     committees.append(committee['name'])

#         for cmte in committees:
#             for i, db_cmte in enumerate(db_committees_names):
#                 if db_cmte.split()[0] in cmte:
#                     print(db_cmte.split()[0], cmte)
#                     cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, db_committees_ids[i]))
#             if cmte == 'Committee on Administration':
#                 print('admin')
#                 cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, 11))
#             elif cmte == "Committee on Veterans' Affairs":
#                 print('veteran')
#                 cur.execute("insert into committee_members_v2 (legislator_id, committee_id) values ({0}, {1})".format(legislator_id, 19))
                    

conn.commit()
conn.close()


                # for committee in committees:
                #     cmte_name = committee
                #     # if cmte_name.startswith('Committee on '):
                #     #     cmte_name = cmte_name[len('Committee on '):]   
                #     # cmte_name                 
                #     cur.execute("select id from committees where congress={0} and name like \"%{1}%\"".format(legislator_congress, cmte_name))
                #     committee_match = cur.fetchall()

                #     if len(committee_match) == 0:
                #         print("select id from committees where congress={0} and name like \"%{1}%\"".format(legislator_congress, cmte_name))

                

                             