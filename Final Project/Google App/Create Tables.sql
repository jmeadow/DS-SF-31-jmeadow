USE predictit;

CREATE TABLE markets (
id int
,name text
,shortname text
,active boolean
,date_end timestamp default CURRENT_TIMESTAMP
,created_at timestamp default CURRENT_TIMESTAMP
,closed_at timestamp default CURRENT_TIMESTAMP
,tickersymbol text
,url text
);

CREATE TABLE contracts
(
	id int
	,market_id int
	,longname text
	,name text
	,shortname text
	,active boolean
	,date_end timestamp default CURRENT_TIMESTAMP
	,created_at timestamp default CURRENT_TIMESTAMP
	,closed_at timestamp default CURRENT_TIMESTAMP
	,tickersymbol text
	,url text
);

CREATE TABLE prices
(
	id serial PRIMARY KEY
	,contract_id int
	,timestamp timestamp default CURRENT_TIMESTAMP
	,buy_no float
	,buy_yes float
	,sell_no float
	,sell_yes float
);