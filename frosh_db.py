import yaml, requests, json, sqlite3
import pandas as pd

with open('config.json') as file:
    config = json.load(file)

industry_amounts_df = pd.read_csv('data/CRP_Categories.csv', sep='\t', usecols=['Catcode'])
industry_amounts_df['Amount'] = 0

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

cur.execute("select id, committee_fec_id, election_year from legislators")
legislators = cur.fetchall()
count = 0

if legislators != ():
    for legislator in legislators:
        legislator_id = legislator[0]
        legislator_committee_fec_id = legislator[1]
        cycle = legislator[2] - 2000 # i.e. 2018 - 2000 = 18, which is how CRP represents cycles in the table name

        cur.execute("select amount, RealCode from indivs_{0} where CmteID='{1}'".format(cycle, legislator_committee_fec_id))
        transactions = cur.fetchall()

        if transactions != ():
            count += 1
            print(count)

            sector_amounts = dict(zip(industry_amounts_df['Catcode'], industry_amounts_df['Amount']))

            for transaction in transactions:
                amount = int(transaction[0])
                sec_code = transaction[1].upper()

                if sec_code in sector_amounts:
                    sector_amounts[sec_code] += amount
            
            for sec, amt in sector_amounts.items():
                cur.execute("insert into sector_amounts (legislator_id, sector, amount) values({0}, '{1}', {2})".format(legislator_id, sec, amt))

conn.commit()
conn.close()