# Anteater installation

* Anteater works by crunching aggregated data from [ENTRADA](https://entrada.sidnlabs.nl),
and storing it on a `PostgreSQL` database
    * (we can later update to a timeseries database)
* As such, _before_ running Anteater, we need to setup a database as bellow.

## 1. PostgreSQL database setup

A. Creating DB and permissions
```sql
--create database
create database anteater;
create user $myuser with encrypted password $PASSWORD;
grant all privileges on database anteater to $myuser;
```
B. Creating tables used by Anteater

```sql
-- store stats per authoritative server
CREATE TABLE authserver (
    epoch_time timestamp without time zone NOT NULL,
    server_name character varying(20) NOT NULL,
    ipv integer NOT NULL,
    nqueries integer NOT NULL,
    avg_rtt numeric(5,2)
);


CREATE TABLE anycastsites (
    epoch_time timestamp without time zone NOT NULL,
    server_name character varying(20) NOT NULL,
    ipv integer NOT NULL,
    nqueries integer NOT NULL,
    nresolvers integer NOT NULL,
    nases integer NOT NULL,
    avg_rtt numeric(5,2)
);

CREATE TABLE hypergiants (
    epoch_time timestamp without time zone NOT NULL,
    asn character varying(30) NOT NULL,
    ipv integer NOT NULL,
    nqueries integer NOT NULL,
    nresolvers integer NOT NULL,
    nsites integer NOT NULL,
    avg_rtt numeric(5,2)
);


CREATE TABLE  resolvers (
    epoch_time timestamp without time zone NOT NULL,
    server_name character varying(11) NOT NULL,
    ipv integer NOT NULL,
    resolvers integer NOT NULL,
    ases integer NOT NULL
);


CREATE TABLE rt_status (
    server_name character varying(20) NOT NULL,
    server_site character varying(20) NOT NULL,
    ipv integer NOT NULL,
    ip_version integer NOT NULL,
    max_ts timestamp without time zone NOT NULL,
    last_complete_ts timestamp without time zone
);

CREATE TABLE rt_results (
    server_name character varying(25) NOT NULL,
    ipv integer NOT NULL,
    last_ts timestamp without time zone NOT NULL,
    rtt numeric(5,2) NOT NULL,
    nqueries integer NOT NULL
);
```

## 2. Anteater configuration

* Clone the repository
* Edit `src/anteater.ini` with the parameters related to our `PostgreSQL`database
and your `ENTRADA` server
  
## 3. Run the scripts
  * (will be added as soon I validate it)