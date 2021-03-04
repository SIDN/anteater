import calendar
import sys
from datetime import date, datetime

from dbutils import conn_impala, conn_postgresql, read_ini


def site_stats(pars):
    today = date.today()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    year = int(year)
    month = int(month)
    day = int(day)

    # figure out the timestamps

    # 1. get the date at minight
    input_date = datetime(year=year, month=month, day=day)

    timestamp = calendar.timegm(input_date.utctimetuple())

    # so this variables define the chunk of data to be analyzed
    # from anteater.ini
    import_delay_hours = pars['anteater'].getint('import_delay')
    bin_size = pars['anteater'].getint('size_bins')
    hour = int(datetime.utcnow().strftime("%H"))

    # entrada store data in timestamp, so we need to convert these time bins to timestamps
    ts1 = timestamp + ((hour - import_delay_hours) * 3600)
    ts2 = timestamp + ((hour - import_delay_hours + bin_size) * 3600)

    entrada_db_table = pars['entrada']['database'] + "." + pars['entrada']['table']

    query = '''  select server,ipv, server_location, count(1) as nqueries, count(distinct(src)) as resolvers,
            count(distinct(asn)) as asn,  avg(tcp_hs_rtt)from entrada.dns 
           where year='''
    query = query + str(year) + " AND  month=" + str(month) + " and  day=" + str(day)
    query = query + " and time between " + str(ts1 * 1000) + " and " + str(ts2 * 1000)
    query = query + "   group by server, ipv, server_location;"

    results = run_query_sites(query, pars)

    resArray = []
    key = str(ts1)
    for k in results:
        resArray.append(key + "," + k)
    return resArray


def store_site_stats(arrayResults):
    # print('store on file, just for debbugging')
    outz = open('results-sites.csv', 'w')
    for k in arrayResults:
        outz.write(k + "\n")
    outz.close()

    print(' start to store on postgresql')
    conn = -1
    try:

        conn = conn_postgresql()
    except:
        print(" conn failed to postgresql")
        e = sys.exc_info()
        print(str(e))

    if conn != -1:
        cur = conn.cursor()

        try:

            for k in arrayResults:
                '''  select server,ipv, server_location, count(1) as nqueries, count(distinct(src)) as resolvers,
                   count(distinct(asn)) as asn,  avg(tcp_hs_rtt) from entrada.dns 
                where year='''
                sp = k.split(",")
                ts = datetime.utcfromtimestamp(int(sp[0]))
                server = sp[1]
                ipv = int(sp[2])
                site = sp[3]
                queries = int(sp[4])
                resolvers = int(sp[5])
                ases = int(sp[6])
                rtt = float(sp[7])
                query = " INSERT INTO anycastsites (epoch_time, server_name, server_site,ipv, nqueries, resolvers,ases, avg_rtt) " \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
                cur.execute(query, (ts, server, site, ipv, queries, resolvers, ases, rtt))

                conn.commit()
            cur.close()
            # close connection
            conn.close()
        except:
            print(" error with postgrsq inserting")
            e = sys.exc_info()
            print(str(e))


def run_query_sites(entradaQuery, pars):
    conn = conn_impala()
    cursor = "-1"
    try:
        cursor = conn.cursor(convert_types=False)
    except:
        print("error cursor")
        e = sys.exc_info()
        print(str(e))

    resDict = dict()
    try:
        if pars['entrada']['request_pool'] != "":
            pool = pars['entrada']['request_pool']
            cursor.execute(entradaQuery, configuration={"REQUEST_POOL": pool})
        else:
            cursor.execute(entradaQuery)
    except:
        print("error executing")
        e = sys.exc_info()
        print(str(e))
        cursor.close()

    # parse results
    results = []
    if cursor != 1:

        print('start to retrieve row  of cursor')
        '''  select server,ipv, server_location, count(1) as nqueries, count(distinct(src)) as resolvers,
           count(distinct(asn)) as asn,  avg(tcp_hs_rtt)from entrada.dns 
        where year='''

        for k in cursor:
            server = str(k[0])
            ipv = str(k[1])
            site = str(k[2])
            nqueries = k[3]
            resolvers = str(k[4])
            ases = str(k[5])
            rtt = k[6]
            rtt = str(rtt).strip()
            rtt = float(rtt)
            value = server + "," + str(ipv) + "," + site + "," + str(nqueries) + "," + str(resolvers) + "," + str(
                ases) + "," + str(
                rtt)
            results.append(value)

    cursor.close()
    conn.close()
    return results


def main():
    config_parameters = read_ini()

    print("starting to pull stats per site data from ENTRADA")
    results = site_stats(config_parameters)
    print("starting to store start per site data on  Postgresql")
    store = store_site_stats(results)


if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  stats_per_server.py")

    else:
        run = main()

