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
    resolvers integer NOT NULL,
    ases integer NOT NULL
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
* `python stats_per_server.py`
  * this script will pull stats per each authoritative server and IP version
  * and will populate one of the tables
  
## 4. Configure `Grafana`
  * Anteater users [Grafana](https://grafana.com/) as visualization tool, so you'll need to set it up 
    * You can read more about it a [Configuring Grafana](https://grafana.com/docs/grafana/latest/administration/configuration/)
* After configuring your new data source in Grafana, you can create a new dashbaord and panel
* To create a panel with number of queries per hour:
  1. Click on `Add Panel`
  1. Click on `Edit SQL ` to edit the query
  1. Add something like :
  ```sql
  SELECT   epoch_time AS "time",
  nqueries AS "YOUR_SERVER_NAME-IPv4"
  FROM authserver
  WHERE
  $__timeFilter(epoch_time) AND
  server_name = 'YOUR_SERVER_NAME'
  and ipv=4
  ORDER BY 1
  ```
* The code above will show a time series of IPv4 queries for this server
* Configure it on `crontab` to run it every hour
* **TODO**: I am working on a script to automate this part, as there may be multiple sites
* **TODO0**: `Anteater` has many more graphs and panes, will add them on the next few days