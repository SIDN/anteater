import calendar
import sys
from datetime import date, datetime

from dbutils import conn_impala, conn_postgresql, read_ini


def server_stats(pars):
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
    import_dealy_hours = pars['anteater']['import_delay']
    bin_size = pars['anteater']['size_bins']
    hour = int(datetime.utcnow().strftime("%H"))

    # entrada store data in timestamp, so we need to convert these time bins to timestamps
    ts1 = timestamp + ((hour - import_dealy_hours) * 3600)
    ts2 = timestamp + ((hour - import_dealy_hours + bin_size) * 3600)

    entrada_db_table = pars['entrada']['database'] + "." + pars['entrada']['table']
    query = ''' select server,ipv, count(1) as  nqueries,avg(tcp_hs_rtt) from '''
    query = query + entrada_db_table + " where year="
    query = query + str(year) + " AND  month=" + str(month) + " and  day=" + str(day)
    query = query + " and time between " + str(ts1 * 1000) + " and " + str(ts2 * 1000) + "  group by server, ipv;"

    results = run_query(query, pars)

    resArray = []
    key = str(ts1)
    for k, v in results.items():
        resArray.append(key + "," + v)

    return resArray


def store_server_stats(arrayResults):
    print('store on file, just for debbugging')
    outz = open('results-nses.csv', 'w')
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
                sp = k.split(",")
                print(sp)
                ts = datetime.utcfromtimestamp(int(sp[0]))
                server = sp[1]
                ipv = sp[2]
                queries = int(sp[3])
                rtt = float(sp[4])

                query = " INSERT INTO authserver (epoch_time, server_name, ipv,nqueries, avg_rtt) " \
                        "VALUES (%s, %s, %s, %s, %s)"
                print(query)
                print(cur.mogrify(query, (ts, server, ipv, queries, rtt)))
                cur.execute(query, (ts, server, ipv, queries, rtt))

                conn.commit()
            cur.close()
            # close connection
            conn.close()
        except:
            print(" error with postgrsq inserting")
            e = sys.exc_info()
            print(str(e))


def run_query(entradaQuery, pars):
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
    results = dict()
    if cursor != 1:

        print('start to retrieve row  of cursor')
        # select server,ipv, count(1) as  nqueries,avg(tcp_hs_rtt) from
        for k in cursor:
            server = str(k[0])
            ipv = str(k[1])
            nqueries = k[2]
            rtt = k[3]
            rtt = str(rtt).strip()
            rtt = float(rtt)
            key = server + "-ipv" + ipv
            value = server + "," + str(ipv) + "," + str(nqueries) + "," + str(rtt)
            results[key] = value

    cursor.close()
    conn.close()
    return results


def main(pars):
    results = server_stats(pars)
    store = store_server_stats(results)


if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  stats_per_server.py")


    else:

        config_parameters = read_ini()
        run = main(config_parameters)
