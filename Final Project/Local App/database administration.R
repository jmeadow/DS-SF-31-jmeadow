library(yaml)
# library(RMySQL)
library(RPostgreSQL)
library(sqldf)
library(beepr)

rm(list = ls())

creds <- yaml.load_file('/Users/jeremy/GA Data Science/DS-SF-31-jmeadow/Final Project/creds.yaml')   #set credentials
postgres <- dbConnect(PostgreSQL(), host = creds$postgres$host, db = creds$postgres$dbname, port = creds$postgres$port, user = creds$postgres$username, password = creds$postgres$password)

# dbnames_q = paste("SELECT datname from pg_database")
# dbnames = dbGetQuery(postgres,dbnames_q)
# dbnames


drop_markets_q = paste("DROP TABLE IF EXISTS markets")
dbSendQuery(postgres,drop_markets_q) #don't drop anything by accident
dbExistsTable(postgres,"markets")

create_markets_q = paste("
	CREATE TABLE markets (
	id int
	,name text
	,shortname text
	,active boolean --need to convert open status to true and otherwise false
	,date_end timestamp --derived from contract date_end
	,created_at timestamp --derived from first status: open
	,closed_at timestamp --derived from last status: open
	,tickersymbol text
	,url text
);")
dbSendQuery(postgres,create_markets_q)
dbExistsTable(postgres,"markets")



drop_contracts_q = paste("DROP TABLE IF EXISTS contracts")
dbSendQuery(postgres,drop_contracts_q) #don't drop anything by accident
dbExistsTable(postgres,"contracts")

create_contracts_q = paste("CREATE TABLE contracts
(
	id int
	,market_id int
	,longname text
	,name text
	,shortname text
	,active boolean --need to convert open status to true and otherwise false. also, is this redundent? not much data to store but still
	,date_end timestamp --from predictit
	,created_at timestamp --derived from first open status
	,closed_at timestamp --derived from last open status
	,tickersymbol text
	,url text
);")
dbSendQuery(postgres,create_contracts_q)
dbExistsTable(postgres,"contracts")


drop_prices_q = paste("DROP TABLE IF EXISTS prices")
dbSendQuery(postgres,drop_prices_q) #don't drop anything by accident
dbExistsTable(postgres,"prices")

create_prices_q = paste("CREATE TABLE prices
(
	id serial PRIMARY KEY --primary key needs to be autoint
	,contract_id int
	,timestamp timestamp
	,buy_no float
	,buy_yes float
	,sell_no float
	,sell_yes float
);")
dbSendQuery(postgres,create_prices_q)
dbExistsTable(postgres,"prices")