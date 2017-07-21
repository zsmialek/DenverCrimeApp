/************************************
*	Creates the tables	    *
*************************************/

DROP TABLE IF EXISTS offense CASCADE;
DROP TABLE IF EXISTS offense_type CASCADE;
DROP TABLE IF EXISTS category CASCADE;

CREATE TABLE category(
	id serial PRIMARY KEY,
	cat_type text
);

CREATE TABLE offense_type( 
	id serial PRIMARY KEY,
	cat_id int REFERENCES category(id),
	off_type text
 );
 
CREATE TABLE offense(
	id numeric PRIMARY KEY,  /* Offense_ID*/
	incident_id numeric,
	type_id int REFERENCES offense_type(id),
	incident_date timestamp,
	address text,
	geo_lon double precision NOT NULL,
	geo_lat double precision NOT NULL,
	district_id int,
	precinct_id int,
	neighborhood_id text,
	is_traffic boolean,
	is_crime boolean
);

/************************************
*	Populating the tables	    *
*	from the master crime table.*
*************************************/

insert into category(cat_type)
select DISTINCT offense_category_id 
from description;

insert into offense_type(cat_id, off_type)
select DISTINCT cat.id, offense_type_id c 
from crime c, category cat
WHERE c.offense_category_id = cat.cat_type;


INSERT INTO offense(id, incident_id, type_id, incident_date, address, geo_lon, geo_lat, district_id, precinct_id, neighborhood_id , is_traffic, is_crime)
SELECT c.offense_id::numeric, c.incident_id::numeric, o.id, to_timestamp(c.first_occurrence_date, 'YYYY-MM-DD hh24:mi:ss'), c.incident_address, c.geo_lon::double precision, c.geo_lat::double precision, c.district_id::integer, c.precinct_id::integer, c.neighborhood_id, c.is_traffic::boolean, c.is_crime::boolean   
FROM crime AS c, offense_type AS o
WHERE c.offense_category_id = o.off_type; 

