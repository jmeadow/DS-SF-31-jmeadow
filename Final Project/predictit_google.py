# PredictIt API Connection, Data Processing, and Upload Script
# Written by Jeremy Meadow
# 2/21/17
# Configured for local Postgres database



## CONNECT TO API AND PULL IN DATA

import numpy as np
import pandas as pd
import json
from urllib2 import urlopen
from pprint import pprint
from IPython.display import display
import os.path #for accessing the json file
import sys
from datetime import datetime
reload(sys)
sys.setdefaultencoding('utf-8') #this is needed to allow special characters in urls and market names

# website = urlopen('https://predictit.org/api/marketdata/ticker/GORSUCH.SCOTUS.NEXTJUSTICE')
website = urlopen('https://predictit.org/api/marketdata/all')
predictit = website.read()


print os.path.isfile('test.json')
target = open('test.json','w')
target.truncate()
target.write(predictit)
target.close()

target = open('test.json','r')
with open('test.json') as data_file:
    predictit = json.load(data_file)
    
pprint(predictit)

print "predictit: "+str(type(predictit))
print 'predictit["Markets"]): '+str(type(predictit["Markets"]))
print 'predictit["Markets"][0]): '+str(type(predictit["Markets"][0]))
print 'predictit["Markets"][0]["Contracts"]: '+str(type(predictit["Markets"][0]["Contracts"]))
print 'predictit["Markets"][0]["Contracts"][0]: '+str(type(predictit["Markets"][0]["Contracts"][0]))

contracts = 0
for x in xrange(0,len(predictit["Markets"])):
    contracts = contracts + len(predictit["Markets"][x]["Contracts"])

print 'Number of markets: '+str(len(predictit["Markets"]))
print 'Number of contracts: '+str(contracts)



### PROCESS API DATA INTO TABLES ###

### Markets ###
markets_id = list()
markets_name = list()
markets_shortname = list()
markets_tickersymbol = list()
markets_url = list()
markets_timestamp = list()
for x in xrange(0,len(predictit["Markets"])):
    markets_id.append(predictit["Markets"][x]["ID"])
    markets_name.append(predictit["Markets"][x]["Name"])    
    markets_shortname.append(predictit["Markets"][x]["ShortName"])    
    markets_tickersymbol.append(predictit["Markets"][x]["TickerSymbol"])    
    markets_url.append(predictit["Markets"][x]["URL"])    
    markets_timestamp.append(predictit["Markets"][x]["TimeStamp"])    
    
markets = pd.DataFrame(data={"id":markets_id,"name":markets_name,"shortname":markets_shortname,"tickersymbol":markets_tickersymbol,"url":markets_url,"timestamp":markets_timestamp})
markets = markets.replace("N/A",np.nan)

### Contracts ###
contracts_id = list()
contracts_market_id = list()
contracts_longname = list()
contracts_name = list()
contracts_shortname = list()
contracts_date_end = list()
contracts_tickersymbol = list()
contracts_url = list()
contracts_timestamp = list()

for x in xrange(0,len(predictit["Markets"])):
    for y in xrange(0,len(predictit["Markets"][x]["Contracts"])):
        contracts_id.append(predictit["Markets"][x]["Contracts"][y]["ID"])
        contracts_market_id.append(predictit["Markets"][x]["ID"])
        contracts_longname.append(predictit["Markets"][x]["Contracts"][y]["LongName"])
        contracts_name.append(predictit["Markets"][x]["Contracts"][y]["Name"])
        contracts_shortname.append(predictit["Markets"][x]["Contracts"][y]["ShortName"])
        contracts_date_end.append(predictit["Markets"][x]["Contracts"][y]["DateEnd"])
        contracts_tickersymbol.append(predictit["Markets"][x]["Contracts"][y]["TickerSymbol"])
        contracts_url.append(predictit["Markets"][x]["Contracts"][y]["URL"])
        contracts_timestamp.append(predictit["Markets"][x]["TimeStamp"])

contracts = pd.DataFrame({"id":contracts_id,"market_id":contracts_market_id,"name":contracts_name,"longname":contracts_longname,"name":contracts_name,"shortname":contracts_shortname,"date_end":contracts_date_end,"tickersymbol":contracts_tickersymbol,"url":contracts_url,"timestamp":contracts_timestamp})
contracts = contracts.replace("N/A",np.nan)

### Prices ###
prices_contract_id = list()
prices_buy_no = list()
prices_buy_yes = list()
prices_sell_no = list()
prices_sell_yes = list()
prices_timestamp = list()

for x in xrange(0,len(predictit["Markets"])):
    for y in xrange(0,len(predictit["Markets"][x]["Contracts"])):
        prices_contract_id.append(predictit["Markets"][x]["Contracts"][y]["ID"])
        prices_buy_no.append(predictit["Markets"][x]["Contracts"][y]["BestBuyNoCost"])
        prices_buy_yes.append(predictit["Markets"][x]["Contracts"][y]["BestBuyYesCost"])
        prices_sell_no.append(predictit["Markets"][x]["Contracts"][y]["BestSellNoCost"])
        prices_sell_yes.append(predictit["Markets"][x]["Contracts"][y]["BestSellYesCost"])
        prices_timestamp.append(predictit["Markets"][x]["TimeStamp"])

prices = pd.DataFrame({"contract_id":prices_contract_id,"buy_no":prices_buy_no,"buy_yes":prices_buy_yes,"sell_no":prices_sell_no,"sell_yes":prices_sell_yes,"timestamp":contracts_timestamp})


# print "Markets Shape: "+str(markets.shape)
# print "Contracts Shape: "+str(contracts.shape)
# print "Prices Shape: "+str(prices.shape)




### IDENTIFY NEW/CLOSED MARKETS AND CONTRACTS ###

import psycopg2

try:
    conn = psycopg2.connect("dbname='postgres' user='jeremy' host='localhost' password=''")
except:
    print "I am unable to connect to the database"
    
cursor = conn.cursor()

### Markets ###
cursor.execute("""select id from markets where active = true""")

db_markets = cursor.fetchall()

active_markets = list()
for x in xrange(0,len(db_markets)):
    active_markets.append(db_markets[x][0])

new_markets = markets.loc[~markets['id'].isin(active_markets)]
new_markets["active"] = ["TRUE"]*len(new_markets)
new_markets.rename(columns={'timestamp':'created_at'}, inplace=True)

closed_markets = [x for x in active_markets if x not in list(markets["id"])]


### Contracts ###  
cursor.execute("""select id from contracts where active = true""")
db_contracts = cursor.fetchall()

active_contracts = list()
for x in xrange(0,len(db_contracts)):
    active_contracts.append(db_contracts[x][0])

new_contracts = contracts.loc[~contracts['id'].isin(active_contracts)]
new_contracts["active"] = ["TRUE"]*len(new_contracts)
new_contracts.rename(columns={'timestamp':'created_at'}, inplace=True)

closed_contracts = [x for x in active_contracts if x not in list(contracts["id"])]


# print contracts.shape
# print new_contracts.shape
# print closed_contracts

# print markets.shape
# print new_markets.shape
# print closed_markets




### MARKETS UPLOAD ###
for x in new_markets.index.values:
    cursor.execute("""
        insert into markets (
            id
            ,name
            ,shortname
            ,active
            ,created_at
            ,tickersymbol
            ,url
        )
        values (
            '"""+str(new_markets["id"][x])+"""'
            ,'"""+str(new_markets["name"][x]).replace("'","''")+"""'
            ,'"""+str(new_markets["shortname"][x]).replace("'","''")+"""'
            ,'"""+str(new_markets["active"][x])+"""'
            ,'"""+str(new_markets["created_at"][x])+"""'
            ,'"""+str(new_markets["tickersymbol"][x])+"""'
            ,'"""+str(new_markets["url"][x]).replace("'","''")+"""'
        )
        """)

### CONTRACTS UPLOAD ###
for x in new_contracts.index.values:
    if pd.isnull(new_contracts["date_end"][x]):
        skip = "--"
    else: 
        skip = ""
    
    
    cursor.execute("""
        insert into contracts (
            id
            ,market_id
            ,longname
            ,name
            ,shortname
            ,active
            """+str(skip)+""",date_end
            ,created_at
            ,tickersymbol
            ,url
        )
        values (
            '"""+str(new_contracts["id"][x])+"""'
            ,'"""+str(new_contracts["market_id"][x])+"""'
            ,'"""+str(new_contracts["longname"][x]).replace("'","''")+"""'
            ,'"""+str(new_contracts["name"][x]).replace("'","''")+"""'
            ,'"""+str(new_contracts["shortname"][x]).replace("'","''")+"""'
            ,'"""+str(new_contracts["active"][x])+"""'
            """+str(skip)+""",'"""+str(new_contracts["date_end"][x])+"""'
            ,'"""+str(new_contracts["created_at"][x])+"""'
            ,'"""+str(new_contracts["tickersymbol"][x])+"""'
            ,'"""+str(new_contracts["url"][x]).replace("'","''")+"""'
        )
        """)

### PRICES UPLOAD ###
for x in prices.index.values:
    
    if pd.isnull(prices["buy_no"][x]):
        skip_bn = "--"
    else: 
        skip_bn = ""
        
    if pd.isnull(prices["buy_yes"][x]):
        skip_by = "--"
    else: 
        skip_by = ""

    if pd.isnull(prices["sell_no"][x]):
        skip_sn = "--"
    else: 
        skip_sn = ""
        
    if pd.isnull(prices["sell_yes"][x]):
        skip_sy = "--"
    else: 
        skip_sy = ""
        
        
    cursor.execute("""
        insert into prices (
            contract_id
            ,timestamp
            """+str(skip_bn)+""",buy_no
            """+str(skip_by)+""",buy_yes
            """+str(skip_sn)+""",sell_no
            """+str(skip_sy)+""",sell_yes
        )
        values (
            '"""+str(prices["contract_id"][x])+"""'
            ,'"""+str(prices["timestamp"][x])+"""'
            """+str(skip_bn)+""",'"""+str(prices["buy_no"][x])+"""'
            """+str(skip_by)+""",'"""+str(prices["buy_yes"][x])+"""'
            """+str(skip_sn)+""",'"""+str(prices["sell_no"][x])+"""'
            """+str(skip_sy)+""",'"""+str(prices["sell_yes"][x])+"""'
        )
        """)




### CLOSE CONTRACTS ###
for x in closed_contracts:
    cursor.execute("""
        update contracts
        set active = false
        ,closed_at = TIMESTAMP WITH TIME ZONE '"""+(contracts["timestamp"][0])+"""'
        where id = """+str(x)+"""
        ;""")

### CLOSE MARKETS ###
for x in closed_markets:
    cursor.execute("""
        update markets
        set active = false
        ,closed_at = TIMESTAMP WITH TIME ZONE '"""+(markets["timestamp"][0])+"""'
        where id = """+str(x)+"""
        ;""")



### COMMIT CHANGES TO DATABASE ###
conn.commit()


### DISPLAY UPDATES MADE ###
display(str(datetime.now())+' update:')
display(str(len(prices))+' prices uploaded.')
display(str(len(list(new_markets["id"])))+' Markets opened: '+str(list(new_markets["id"])))
display(str(len(closed_markets))+' Markets closed: '+str(closed_markets))
display(str(len(list(new_contracts["id"])))+' Contracts opened: '+str(list(new_contracts["id"])))
display(str(len(closed_contracts))+' Contracts closed: '+str(closed_contracts))