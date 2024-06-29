###################
## https://www.py4e.com/lessons/dataviz
## Data Visualization

import urllib.request, urllib.parse, urllib.error
import http
import sqlite3
import json
import time
import ssl
import sys

# Google API (requires API key)
# serviceurl = "http://maps.googleapis.com/maps/api/geocode/json?"
# If you are in China this URL might work (with key):
# serviceurl = "http://maps.google.cn/maps/api/geocode/json?"

api_key = '******'

if api_key is False:
    serviceurl = "http://python-data.dr-chuck.net/geojson?"
else:
    serviceurl = "https://maps.googleapis.com/maps/api/geocode/json?"

# Deal with SSL certificate anomalies Python > 2.7
# scontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
#scontext = None

conn = sqlite3.connect('geodata.sqlite')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS Locations (address TEXT, geodata TEXT)''')

#ignore SSL certificate errors
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

fh = open("where.data")
count = 0
for line in fh:
    if count > 200 : 
        print('Retrieved 200 locations, restart to retrieve more')
        break
    address = line.strip()
    print('')
    cur.execute('''SELECT geodata FROM Locations WHERE address= ?''', 
        (memoryview(address.encode()), ))

    try:
        data = cur.fetchone()[0]
        print("Found in database ",address)
        continue
    except:
        pass
    
    params = dict()
    params['address']=address

    if api_key is not False: params['key'] = api_key

    print('Resolving', address)
    url = serviceurl + urllib.parse.urlencode(params)
    urlprint = serviceurl + urllib.parse.urlencode({'address':address,'key':'xxxxxxxx'})
    print('Retrieving', urlprint)
    uh = urllib.request.urlopen(url,context=ctx)
    data = uh.read().decode()
    print('Retrieved',len(data),'characters',data[:20].replace('\n',' '))
    count = count + 1
    try: 
        js = json.loads(data)
        # print js  # We print in case unicode causes an error
    except: 
        print(data)
        continue

    if 'status' not in js or (js['status'] != 'OK' and js['status'] != 'ZERO_RESULTS') : 
        print('==== Failure To Retrieve ====')
        print(data)
        continue

    cur.execute('''INSERT INTO Locations (address, geodata) 
            VALUES ( ?, ? )''', ( memoryview(address.encode()),memoryview(data.encode()) ) )
    conn.commit() 
    if count % 2500 == 0 :
        print('Pausing for a bit...')
        time.sleep(60)

print("Run geodump.py to read the data from the database so you can visualize it on a map.")
