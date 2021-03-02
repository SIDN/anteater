# Anteater
_Real-time Authoritative Server Monitoring with passive measurements._ 

We presented `Anteater` recently at:

* [DNS-OARC 34](https://indico.dns-oarc.net/event/37/contributions/812/)
* Please refer to our [technical report on DNS/RTT measurements](https://www.isi.edu/~johnh/PAPERS/Moura20a.pdf) 

We have been using `Anteater` at [SIDN](https://sidn.nl) for more than 1 year now.


## Status
* 2021-03-02: **The first dashboard** is operational!  See [demo.md](src/grafana-dashboards/demo/demo.md) for more!
  * We will keep on adding more dashboards in the coming days, namely:
    1. One dashboard per authoritative server
    1. One dashboard for HyperGiants and your favorite ASes
* Follow [INSTALL.md](INSTALL.md) for how to configure it


## Next steps:
*  2021-03-02: Refactor code to retrieve  RTT statistics per Anycast  locations (site) 



![Anteater](resources/anteater-logo.png)


* <a href="http://www.freepik.com"> Anteater image designed by brgfx / Freepik</a>
