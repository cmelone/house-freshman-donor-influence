#TODO: assign each committee/subcommittee to a crp sector code
import requests, json, sqlite3
from collections import Counter

with open('pdfs/112_subcommittees.txt') as f:
    subcmtes_read = f.read()
    subcmtes = []
    cmtes = []
    for su in subcmtes_read.splitlines():
        if su[0] != '#':
            subcmtes.append(su.strip())
        else:
            cmtes.append(su[1:].strip())

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

cur.execute("select full_name, alt_full_name, id, congress from legislators where congress=112 or congress=113 or congress=114")

with open('pdfs/112_cmtes.txt') as file:
    data = file.read()
lines = data.splitlines()
legislators = cur.fetchall()
count = 0

rep_subcmte_arr = []

if legislators != ():
    for legislator in legislators:
        legislator_id = legislator[2]
        congress = legislator[3]

        if legislator[1] != None:
            name = legislator[1] # alt first name
        else:
            name = legislator[0] # regular first name

        backwards_array = []
        subcmte_arr = []

        for i, line in enumerate(lines):
            backwards_array.append(line)
            
            if name in line:
                found_subcmte = False
                found_cmte = False
                subcmte_dict = []
                for j, item in enumerate(reversed(backwards_array)):
                    if  len(item.strip()) > 0:
                        if found_subcmte == False and item.strip().endswith(', Chair'):
                            subcmte = list(reversed(backwards_array))[j+2].strip()
                            if subcmte not in subcmtes:
                                subcmte = None
                            found_subcmte = True
                        if found_cmte == False and item.strip() in cmtes:
                            if subcmte != None:
                                subcmte_arr.append({'parent_committee': item.strip(), 'subcommittee': subcmte})
                            found_cmte = True
        rep_subcmte_arr.append({'id': legislator_id, 'subcommittees': subcmte_arr, 'congress': congress})


for entry in rep_subcmte_arr:
    for subcmte in entry['subcommittees']:
        cur.execute("select id from committees where congress={0} and name='{1}'".format(entry['congress'], subcmte['parent_committee']))
        cmte_match = cur.fetchall()

        if cmte_match != ():
            cur.execute("select id from subcommittees where congress={0} and name='{1}' and parent_id={2}".format(entry['congress'], subcmte['subcommittee'], cmte_match[0][0]))
            subcmte_match = cur.fetchall()

            if subcmte_match != []:
                cur.execute("insert into subcommittee_members_v2 (legislator_id, subcommittee_id) values({0}, {1})".format(entry['id'], subcmte_match[0][0]))

conn.commit()
conn.close()



# congresses = [112, 113, 114, 115, 116]
# congress_sub_committees_arr = []

# for congress in congresses:
#     url = 'https://api.propublica.org/congress/v1/{0}/house/committees.json'.format(congress)
#     congress_sub_committees_arr.append({'congress': congress, 'subcommittees': requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()})

# final_subcmte_arr = []

# for rep in rep_subcmte_arr:
#     rep_id = rep['id']
#     rep_congress = rep['congress']
#     rep_subcommittees = rep['subcommittees']
#     final_rep_subcommitees = []

#     for c in congress_sub_committees_arr:
#         if rep_congress == c['congress']:
#             for cmte in c['subcommittees']['results'][0]['committees']:
#                 for subcmte in cmte['subcommittees']:
#                     if subcmte['name'] in rep_subcommittees:
#                         final_rep_subcommitees.append(subcmte['name'])
#     final_subcmte_arr.append({'id': rep_id, 'subcommittees': final_rep_subcommitees})

# print(rep_subcmte_arr)
# print(final_subcmte_arr)





# for rep in rep_subcmte_arr:
#     congress = rep['congress']

#     url = 'https://api.propublica.org/congress/v1/{0}/house/committees.json'.format(congress)
#     resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()
#     for res in resp:


# url = 'https://api.propublica.org/congress/v1/members/{0}.json'.format(legislator_bioguide_id)
# 33resp = requests.get(url, headers={'X-API-Key': config['PROPUBLICA_API_KEY']}).json()


# arr=[]
# b=[]
# if legislators != ():
#     for legislator in legislators:
#         b.append(legislator[0])
#         if legislator[1] != None:
#             name = legislator[1]
#         else:
#             name = legislator[0]
#         # print(legislator[0], name)
#         bb=[]
#         #print(name)
#         for i, line in enumerate(lines):
#             bb.append(line)
#             if name in line:
#                 # print({'jjjjj': list(reversed(bb))})
#                 satisfied = False
#                 for b, item in enumerate(reversed(bb)):
#                     if  satisfied == False and len(item.strip()) > 0:
#                         #print(item.strip())
#                         if item.strip().endswith(', Chair'):
#                             # print(list(reversed(bb))[0])
#                             print(list(reversed(bb))[b+2])
#                             satisfied = True

#                 arr.append(name)





#print(dict(Counter(arr)))
#e=list(dict(Counter(arr)))
#print(len(Counter(arr)))