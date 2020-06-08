import json, sqlite3, sys, requests

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

# get duplicate subcommittees across congresses
cur.execute("select * from subcommittees")
subcommittees_resp = cur.fetchall()

subcmtes_entries = []
collect = []

if len(subcommittees_resp) > 0:
    for subcmte_1 in subcommittees_resp:
        subcmte_1_name = subcmte_1[2]
        subcmte_1_parent = subcmte_1[1]

        if {'parent': subcmte_1_parent, 'name': subcmte_1_name} not in collect:
            subcmte_1_id = subcmte_1[0]
            subcmte_1_congress = subcmte_1[3]

            duplicates_ids = []
            duplicates_ids.append(subcmte_1_id)


            for subcmte_2 in subcommittees_resp:
                subcmte_2_id = subcmte_2[0]
                subcmte_2_parent = subcmte_2[1]
                subcmte_2_name = subcmte_2[2]
                subcmte_2_congress = subcmte_2[3]   

                if (subcmte_1_name == subcmte_2_name) and (subcmte_1_parent == subcmte_2_parent) and (subcmte_1_congress != subcmte_2_congress):
                    append = True
                    duplicates_ids.append(subcmte_2_id)

            
            collect.append({'parent': subcmte_1_parent, 'name': subcmte_1_name})
            subcmtes_entries.append({'name': subcmte_1_name, 'parent_id': subcmte_1_parent, 'entries': duplicates_ids})

len(subcmtes_entries) # <--- unique # of committees across the 5 congresses

for subcmte in subcmtes_entries:
    cur.execute("select name from committees where id={0}".format(subcmte['parent_id']))
    parent_name = cur.fetchall()
    subcmte_name = subcmte['name']
    if len(subcommittees_resp) > 0:
        print('Parent Committee: {0}. Subcommittee: {1}'.format(parent_name[0][0], subcmte_name))
        sector_code = input('Provide sector code or type NA if there is no match: ')
        subcmte['sector_code'] = sector_code

# TODO: manually assign sector codes (the general ones though) to the committees table

for subcmte in subcmtes_entries:
    for id_ in subcmte['entries']:
        cur.execute("UPDATE subcommittees set sector_code = '{0}' where id={1}".format(subcmte['sector_code'], id_))
print('Database updated with sector codes')

conn.commit()
conn.close()

# if __name__ == '__main__':
#     globals()[sys.argv[1]]() # run function from command line