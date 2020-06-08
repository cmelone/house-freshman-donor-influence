# this script identifies the legislators that need to have an alt_full_name added to their db entry
# the legislator's full names are collected from legislators.yaml, but the congressional directory file may have different names for those legislators
# this code essentially gets the full names for the legislators in a certain congress, searches those names in the file, and then outputs the names
# that weren't sound
# when running, change the first cur.execute and with open('pdfs/114_cmtes.txt') as file: to reflect the correct congress

import requests, json, sqlite3
from collections import Counter

with open('config.json') as file:
    config = json.load(file)

conn = sqlite3.connect(config['SQLITE_PATH'])
cur = conn.cursor()

cur.execute("select full_name, alt_full_name from legislators where congress=114")

with open('pdfs/114_cmtes.txt') as file:
    data = file.read()
lines = data.splitlines()
legislators = cur.fetchall()

if legislators != ():
    for legislator in legislators:
        if legislator[1] != None:
            name = legislator[1] # alt first name
        else:
            name = legislator[0] # regular first name
        f = False
        for line in lines:
            if name in line:
                f = True
        if f == False:
            print(name)
