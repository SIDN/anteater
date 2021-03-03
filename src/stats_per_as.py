import calendar
import sys
from datetime import date, datetime

from dbutils import conn_impala, conn_postgresql, read_ini

def makeASList(pars):
    ases4query=" ("

    asGroup=pars['anteater']['ases_to_monitor']
    for i in asGroup:
        asn=i.split("-")[0].strip()
        ases4query=ases4query +"'" + asn +"',"

    ases4query=ases4query[:-1]
    ases4query=ases4query+") "
    return ases4query

def as_stats(pars):
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

    query = ''' select  asn,server, ipv,  count(1) as nqueries, count(distinct(src)) as resolvers, 
            count(distinct(server_location)) as nsites, avg(tcp_hs_rtt) as avgRTT  from entrada.dns 
            where year='''
    query = query + str(year) + " AND  month=" + str(month) + " and  day=" + str(day)
    query = query + " and time between " + str(ts1 * 1000) + " and " + str(ts2 * 1000) + " and asn in "

    ases=makeASList(pars)

    query= query + ases +  " group by asn, server, ipv;"



    results = run_query(query, pars)

    resArray = []
    key = str(ts1)
    for k in results:
        resArray.append(key + "," + k)

    return resArray


def store_as_stats(arrayResults):
    print('store on file, just for debbugging')
    outz = open('results-ases.csv', 'w')
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
            query = ''' select  asn,server, ipv,  count(1) as nqueries, count(distinct(src)) as resolvers, 
                    count(distinct(server_location)) as nsites, avg(tcp_hs_rtt) as avgRTT  from entrada.dns 
                    where year='''
            for k in arrayResults:
                sp = k.split(",")
                print(sp)
                ts = datetime.utcfromtimestamp(int(sp[0]))
                asn=sp[1]
                server = sp[2]
                ipv = sp[3]
                queries = int(sp[4])
                resolvers = int(sp[5])
                sites = int(sp[6])
                rtt=""
                try:
                    rtt = float(sp[7])
                except:
                    rtt=None

                query = " INSERT INTO ASes (epoch_time, asn, server_name, ipv, queries, resolvers,sites, avg_rtt) " \
                        "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                #print(cur.mogrify(query, (ts, asn, server, ipv, queries, resolvers, sites, rtt))
                cur.execute(query, (ts, asn, server, ipv, queries, resolvers, sites, rtt))

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
    results =[]
    if cursor != 1:

        print('start to retrieve row  of cursor')
        ''' 
            select  asn,server, ipv,  count(1) as nqueries, count(distinct(src)) as resolvers, 
            count(distinct(server_location)) as nsites, avg(tcp_hs_rtt) as avgRTT 
        '''
        for k in cursor:
            asn=str(k[0])
            server = str(k[1])
            ipv = str(k[2])
            queries = str(k[3])
            resolvers = str(k[4])
            sites=str(k[5])
            rtt = k[6]
            rtt = str(rtt).strip()
            #handling cases of no TCP queries and thus no RTT
            if rtt!="None":
                rtt = str(float(rtt))
            else:
                rtt="Null"
            value = asn + "," + server+ "," + ipv+ "," + queries + "," + resolvers + "," + sites + "," + rtt
            results.append(value)

    cursor.close()
    conn.close()
    return results





def main(pars):
    print("starting to pull stats per AS data from ENTRADA")
    results = as_stats(pars)
    print("starting to store start per AS data on  Postgresql")
    store = store_as_stats(results)


if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  stats_per_as.py")


    else:

        config_parameters = read_ini()
        run = main(config_parameters)
