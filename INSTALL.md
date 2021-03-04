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
    server_site character varying(20) NOT NULL,
    ipv integer NOT NULL,
    nqueries integer NOT NULL,
    resolvers integer NOT NULL,
    ases integer NOT NULL,
    avg_rtt numeric(5,2)
);

CREATE TABLE ASes (
    epoch_time timestamp without time zone NOT NULL,
    asn character varying(30) NOT NULL,
    server_name character varying(20) NOT NULL,
    ipv integer NOT NULL,
    queries integer NOT NULL,
    resolvers integer NOT NULL,
    sites integer NOT NULL,
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
* configure `cron` to run the script below using the same frequency you specify in [anteater.ini](src/anteater.ini):
    * `python anteater.py`
    
  
## 4. Configure `Grafana`

* **Note**: you need to do this only once, or whenever you update `anteater.ini` or more sites are added to your anycast services.
* Anteater uses [Grafana](https://grafana.com/) as visualization tool, so you'll need to set it up  
  * (we do not cover  it here, but follow [Configuring Grafana](https://grafana.com/docs/grafana/latest/administration/configuration/)
 to learn how to do it)
* Next step is to confiugure the dashboards, which you can do manually or you can use our tool to export 
a dashboard in `JSON` format, that you can later [import into Grafana](https://grafana.com/docs/grafana/latest/dashboards/export-import/).

### 4.1 Overview Dashboard

  * This dashboard shows in one page only all authoritative server, aggregated.
  * To generate it, execute the follow steps:
      1. go to `src/grafana-dasboards/stats_per_server/`
      2. Run `python dashboard-auth-servers.py`
      3. Retrieve `export/authservers.json` and  [import it into Grafana](https://grafana.com/docs/grafana/latest/dashboards/export-import/). 

## 4.2 Anycast sites Dashboard

* Now we need to generate **one dashboard** per authoritative server, in which all 
anycast sites are shown.
  
* To generate it, do the following steps:
    1. go to `src/grafana-dasboards/stats_per_site/`
    2. Run `python dashboard-sites.py`
    3. Retrieve `export/$SERVER.json` and  [import it into Grafana](https://grafana.com/docs/grafana/latest/dashboards/export-import/).
        * there will be multiple dashboards, one per auth server.

## 4.2 ASes Dashboard

* Now we need to generate **one dashboard** per Autonomous System we are interested in monitoring
* You can **add your ASes of choice** on [anteater.ini](src/anteater.ini), using the variable
  `ases_to_monitor`
  
* To generate it, do the following steps:
    1. go to `src/grafana-dasboards/stats_per_as/`
    2. Run `python dashboard-ases.py`
    3. Retrieve `export/ases.json` and  [import it into Grafana](https://grafana.com/docs/grafana/latest/dashboards/export-import/).
    
