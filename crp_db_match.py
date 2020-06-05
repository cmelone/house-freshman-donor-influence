import sqlite3, sys, json
import pandas as pd

with open('config.json') as file:
    config = json.load(file)

df = pd.read_csv('data/candidates_fec_cmte.csv')
df['SEC_DONATIONS'] = ''
industry_df = pd.read_csv('CRP_Categories.csv', sep='\t')

industry_amounts_df = pd.read_csv('CRP_Categories.csv', sep='\t', usecols=['Catcode'])
industry_amounts_df['Amount'] = 0
sector_amounts_dict = dict(zip(industry_amounts_df['Catcode'], industry_amounts_df['Amount']))

#conn = sqlite3.connect(crp.db

cur = conn.cursor()

# for row in df.itertuples():
#     cycle = row.Cycle - 2000 
#     query = "select amount from indivs_{0} where CmteID='{1}'".format(cycle, row.FEC_CMTE_ID)
#     cur.execute(query)
#     if cur.fetchall() == ():
#         print(row.FEC_CMTE_ID)
#     else:
#         print('ok')
count = 0
for row in df.itertuples():
    cycle = row.Cycle - 2000
    cmte_id = row.FEC_CMTE_ID
    cur.execute("select amount, RealCode from indivs_{0} where CmteID='{1}'".format(cycle, cmte_id))
    output = cur.fetchall()

    if output != ():
        iter_sec_amts = dict(zip(industry_amounts_df['Catcode'], industry_amounts_df['Amount']))
        #industry_amounts_df = pd.read_csv('CRP_Categories.csv', sep='\t', usecols=['Catcode'])
        #industry_amounts_df['Amount'] = 0
        for record in output:
            sec_code = record[1].upper()
            amount = int(record[0])
            if sec_code in iter_sec_amts:
                iter_sec_amts[sec_code] += amount
            #industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec_ind_code, 'Amount'] += amount
        # put the industry_amounts_df inside df['SEC_DONATIONS] NO

        # create a db table that has a list of records of all the sector amounts
        # columns: user identifier (committee?), amount, and sector
        #print(iter_sec_amts )
        for key, val in iter_sec_amts.items():
            cur.execute("insert into sector_amount_totals (cmte_id, sector, amount) values('{0}', '{1}', {2})".format(cmte_id, key, val))
    # print(iter_sec_amts)

    print(count, row.Freshman)
    count += 1
    # print(row.Freshman)
conn.commit()        


#query = "select amount, RealCode from indivs_{0} where CmteID='{1}' and Cycle='{2}'".format('18', 'C00649913', '2018')
#cur.execute(query)

# output = cur.fetchall()
# industry_amounts_df = pd.read_csv('CRP_Categories.csv', sep='\t', usecols=['Catcode'])
# industry_amounts_df['Amount'] = 0

# for record in output:
#     sec_ind_code = record[1]
#     amount = int(record[0])
#     industry_amounts_df.loc[industry_amounts_df['Catcode'] == sec_ind_code, 'Amount'] += amount

conn.close()
print()
#industry_amounts_df.to_csv('final/span.csv', encoding='utf-8', index=False)
#explain query plan select amount from indivs_18 where CmteID='C00649913';