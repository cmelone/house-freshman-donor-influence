import json, sqlite3, sys, requests
import pandas as pd

with open('config.json') as file:
    config = json.load(file)

industry_amounts_df = pd.read_csv('data/CRP_Categories.tsv', sep='\t', usecols=['Catcode', 'Catname'])

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

def subcommittees():
    cur.execute("select id, full_name from legislators")
    legislators = cur.fetchall()
    count_unique = 0
    count_total = 0
    did_it_again_count = 0
    if len(legislators) > 0:
        for legislator in legislators:
            did_it_again = False
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
            # print("{0} top 10 sectors: ".format(legislator_name))
            # for i, sec in enumerate(top_sectors):
            #     print("{0}. {1}: ${2}".format(i+1, industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))

            cur.execute("select subcommittee_id from subcommittee_members_v2 where legislator_id={0}".format(legislator_id))
            subcommittees_match = cur.fetchall()
            legislator_subcommittees_match = []
            if len(subcommittees_match) > 0:
                for subcmte in subcommittees_match:
                    subcmte_id = subcmte[0]
                    cur.execute("select name, sector_code from subcommittees where id={0}".format(subcmte_id))
                    subcommittees = cur.fetchall()
                    if len(subcommittees) > 0:
                            for subcmte_2 in subcommittees:
                                sector_s = subcmte_2[1] # sector_s means sector(s)
                                name = subcmte_2[0]
                                legislator_subcommittees_match.append({'name': name, 'sector_s': sector_s})
            
            matched_arr = []
            matched = False 
            for sec in top_sectors:
                for subcmte in legislator_subcommittees_match:
                    if sec['sector'] in subcmte['sector_s']:
                        if matched == True: # has already had a sector code from top donor linked to subcommittee membership
                            did_it_again = True
                            count_total += 1
                            matched_arr.append({'sector': sec['sector'], 'amount': sec['amount'], 'subcommittee': subcmte['name']})
                            #print("MATCH AGAIN {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
                        if matched == False:
                            #print("MATCH {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
                            matched_arr.append({'sector': sec['sector'], 'amount': sec['amount'], 'subcommittee': subcmte['name']})
                            count_unique += 1
                            count_total += 1
                            matched = True    

            # if len(matched_arr) == 0:
            #     #print('Rep. {0} did not have any links between top donors by sector and subcommittee membership.'.format(legislator_name))
            # else:
            #     #print('Rep {0} had the following links between top donors by sector and subcommittee membership: '.format(legislator_name))
                
            #     for match in matched_arr:
            #         #print('Sector: {0}. Sector Code: {1}. Amount Donated By Sector: ${2}. Linked Subcommittee: {3}'.format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == match['sector']].values[0][1], match['sector'], match['amount'], match['subcommittee']))   
            if did_it_again == True:
                did_it_again_count += 1             
    print(did_it_again_count) # how many of them had influence of more than one sector
    print('Total Instances of Joining Subcommittees: {0} Unique Instances of Joining Subcommittees: {1}'.format(count_total, count_unique))
    conn.close()


def committees():
    cur.execute("select id, full_name from legislators")
    legislators = cur.fetchall()
    count_unique = 0
    count_total = 0
    test_arr = []
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

            cur.execute("select committee_id from committee_members_v2 where legislator_id={0}".format(legislator_id))
            committees_match = cur.fetchall()
            legislator_committees_match = []
            if len(committees_match) > 0:
                for cmte in committees_match:
                    cmte_id = cmte[0]
                    cur.execute("select name, sector_code from committees where id={0}".format(cmte_id))
                    committees = cur.fetchall()
                    if len(committees) > 0:
                            for cmte_2 in committees:
                                sector_s = cmte_2[1] # sector_s means sector(s)
                                name = cmte_2[0]
                                legislator_committees_match.append({'name': name, 'sector_s': sector_s})
            
            matched_arr = []
            matched = False 
            for sec in top_sectors:
                for cmte in legislator_committees_match:
                    if sec['sector'] in cmte['sector_s']:
                        if matched == True: # has already had a sector code from top donor linked to subcommittee membership
                            count_total += 1
                            matched_arr.append({'sector': sec['sector'], 'amount': sec['amount'], 'committee': cmte['name']})
                            #print("MATCH AGAIN {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
                        if matched == False:
                            #print("MATCH {0}: ${1}".format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec['sector']].values[0][1], sec['amount']))
                            matched_arr.append({'sector': sec['sector'], 'amount': sec['amount'], 'committee': cmte['name']})
                            count_unique += 1
                            count_total += 1
                            matched = True    

            if len(matched_arr) == 0:
                int('1')
                #print('Rep. {0} did not have any links between top donors by sector and committee membership.'.format(legislator_name))
            else:
                #print('Rep {0} had the following links between top donors by sector and subcommittee membership: '.format(legislator_name))
                bruh.append(matched_arr)
                #for match in matched_arr:

                    #print('Sector: {0}. Sector Code: {1}. Amount Donated By Sector: ${2}. Linked Committee: {3}'.format(industry_amounts_df.loc[industry_amounts_df['Catcode'] == match['sector']].values[0][1], match['sector'], match['amount'], match['committee']))                

    print('Total Instances of Joining Committees: {0} Unique Instances of Joining Committees: {1}'.format(count_total, count_unique))
    #print(test_arr)
    conn.close()

if __name__ == '__main__':
    globals()[sys.argv[1]]() # run function from command line