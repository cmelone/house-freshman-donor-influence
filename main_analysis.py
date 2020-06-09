import json, sqlite3, sys, requests
import pandas as pd

with open('config.json') as file:
    config = json.load(file)


industry_amounts_df = pd.read_csv('data/CRP_Categories.tsv', sep='\t', usecols=['Catcode', 'Catname'])

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

cur.execute("select id, full_name from legislators")
legislators = cur.fetchall()
count_unique = 0
count_total = 0
if len(legislators) > 0:
    for legislator in legislators:
        legislator_id = legislator[0]
        legislator_name = legislator[1]
        cur.execute("select sector, amount from sector_amounts where legislator_id={0}".format(legislator_id))
        sector_amounts_match = cur.fetchall()
        sector_amounts_arr = []
        if len(sector_amounts_match) > 0:
            for sector_amount in sector_amounts_match:
                amount = sector_amount[1]
                sector = sector_amount[0]

                sector_amounts_arr.append({'sector': sector, 'amount': amount})

        new_arr = sorted(sector_amounts_arr, key=lambda k: k['amount'], reverse=True)

        top_sectors = new_arr[:10] # top 10 for the moment
        # print the top 10 sectors for the legislator
        #print("{0} top 10 sectors: ".format(legislator_name))
        #for i, sec in enumerate(top_sectors):
            #print("{0}. {1}: ${2}".format(i+1, industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
        legislator_subcommittee_sectors_str = ''

        cur.execute("select subcommittee_id from subcommittee_members_v2 where legislator_id={0}".format(legislator_id))
        subcommittees_match = cur.fetchall()
        legislator_subcommittees_match = []
        if len(subcommittees_match) > 0:
            for subcmte in subcommittees_match:
                subcmte_id = subcmte[0]
                cur.execute("select name, sector_code from subcommittees where id={0}".format(subcmte_id))
                subcommittees = cur.fetchall()
                if len(subcommittees) > 0:
                        for subcmte in subcommittees:
                            sector_s = subcmte[1] # sector_s means sector(s)
                            name = subcmte[0]
                            legislator_subcommittees_match.append({'name': name, 'sector_s': sector_s})
        
        matched_arr = []
        matched = False 
        for sec in top_sectors:
            for subcmte in legislator_subcommittees_match:
                if sec['sector'] in subcmte['sector_s']:
                    if matched == True: # has already had a sector code from top donor linked to subcommittee membership
                        count_total += 1
                        matched_arr.append({'sector': sec['sector'], 'amount': sec['amount'], 'subcommittee': subcmte['name']})
                        #print("MATCH AGAIN {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
                    if matched == False:
                        #print("MATCH {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
                        matched_arr.append({'sector': sec['sector'], 'amount': sec['amount'], 'subcommittee': subcmte['name']})
                        count_unique += 1
                        count_total += 1
                        matched = True    

        if len(matched_arr) == 0:
            print('Rep. {0} did not have any links between top donors by sector and subcommittee membership.'.format(legislator_name))
        else:
            print('Rep {0} had at least one link between top donors by sector and subcommittee membership: '.format(legislator_name))

            for match in matched_arr:
                print('Sector: {0}. Sector Code: {1}. Amount Donated By Sector: {2}. Linked Subcommittee: {3}'.format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == match['sector']].values[0][1], match['sector'], match['amount'], match['subcommittee']))                

            # if sec['sector'] in legislator_subcommittee_sectors_str: # probably need to get the exact subcommittee to include in this line
            #     if corrupt == True:
            #         count_total += 1
            #         print("MATCH AGAIN {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
            #     if corrupt == False:
            #         print("MATCH {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
            #         count_unique += 1
            #         count_total += 1
            #         corrupt = True


print('Total Instances of Joining Subcommittees: {0} Unique Instances of Joining Subcommittees: {1}'.format(count_total, count_unique))
conn.close()