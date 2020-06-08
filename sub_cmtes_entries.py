import json, sqlite3, sys, requests

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

# this code takes the text files that were manually created from the congressional directory pdfs, then adds the found committees and subcommittees into their respective tables

def text_files():
    congresses = [112, 113, 114]
    for congress in congresses:
        with open('pdfs/{0}_subcommittees.txt'.format(congress)) as f:
            subcmtes_read = f.read()
            collect = []
            sub_and_cmtes_arr = []
            hash_cmte = ''
            subcmtes_split = subcmtes_read.splitlines()
            for i, su in enumerate(subcmtes_split):
                if su[0] == '#':
                    hash_cmte = su[1:].strip()
                else:
                    collect.append(su.strip())
                if i == len(subcmtes_split)-1: # last committee in list
                    sub_and_cmtes_arr.append({'committee': hash_cmte, 'subcommittees': collect})
                if (i+1) < len(subcmtes_split):
                    if subcmtes_split[i+1][0] == '#':
                        sub_and_cmtes_arr.append({'committee': hash_cmte, 'subcommittees': collect})
                        collect = []
                        hash_cmte = ''
                
        for sub_and_cmtes in sub_and_cmtes_arr:
            for sub in sub_and_cmtes['subcommittees']:
                # if a committee by the name already exists in the committee database, then don't add it (committees are constant across all 5 congresses) otherwise, add it to the committees table
                cur.execute("select id from committees where name=\"{0}\"".format(sub_and_cmtes['committee']))
                committee_match = cur.fetchall()
                if len(committee_match) > 0:
                    parent_id = committee_match[0][0]
                else:
                    cur.execute("insert into committees (name) values (\"{0}\")".format(sub_and_cmtes['committee']))
                    parent_id = cur.lastrowid                
                cur.execute("insert into subcommittees (parent_id, name, congress) values ({0}, \"{1}\", {2})".format(parent_id, sub, congress))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    globals()[sys.argv[1]]() # run function from command line