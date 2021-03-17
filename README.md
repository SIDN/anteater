# Anteater
_Real-time Authoritative Server Monitoring with passive DNS measurements._ 

We presented `Anteater` recently at:

* [DNS-OARC 34](https://indico.dns-oarc.net/event/37/contributions/812/)
* Please refer to our [technical report on DNS/RTT measurements](https://www.isi.edu/~johnh/PAPERS/Moura20a.pdf) 

We have been using `Anteater` at [SIDN](https://sidn.nl) for more than 1 year now.

## To install it
* Read  [INSTALL.md](INSTALL.md) for how to configure it

## To run it for on specific date:
  * Say you had an issue with your `ENTRADA` data, and when you ran `anteater` the data was incomplete.
  * You can re-run now `anteater` for any given date: simply run `rerun_for_given_date.py`, using as parameter the day you want, as `python rerun_for_given_date.py 20210310`
    * The command above will **delete** from PostgreSQL all data for the specified date (2021-03-10)
    * Then, it will re-run  queries agian for this specific day,and repopulate the database based on now complete data from  `ENTRADA`.

## Demo (screenshots):

* See [demo.md](src/grafana-dashboards/demo/demo.md)  for your dashboards will look like


## Changelog

* 2021-03-04: Fully automated via `src/anteater.py`.
* 2021-03-04: **The third dashboard** is operational, which monitors individual ASes. See [demo.md](src/grafana-dashboards/demo/demo.md) for more
* 2021-03-04: **The second dashboard** is operational, which monitors anycast sites. See [demo.md](src/grafana-dashboards/demo/demo.md) for more
* 2021-03-02: **The first dashboard** is operational!  


![Anteater](resources/anteater-logo.png)


* <a href="http://www.freepik.com"> Anteater image designed by brgfx / Freepik</a>
