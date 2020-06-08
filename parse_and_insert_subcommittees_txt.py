# this script takes a file generated from the congressional directory pdf for a certain congress, and a file that has a list of all subcommittees and committees for that congress
# it matches each legislator from the specific congress and adds their entries to the database
# what to change: open('pdfs/112_subcommittees.txt') as f: and  with open('pdfs/112_cmtes.txt') as file: to match the congress,
# and the first cur.execute command to only match the congress

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

# this takes the subcommittees reported for the 112, 113, and 114 congresses and adds them to the subcommittee member databases
# the script that actually adds the subcommittee names into the database needs to be ran before this

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
