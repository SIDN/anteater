import sys
from dbutils import  conn_postgresql, read_ini
from datetime import datetime, timedelta
import calendar
from stats_per_as import makeASList, run_query as runQueryPerAS,store_as_stats
from stats_per_server import run_query as run_query_per_server,store_server_stats
from stats_per_site import run_query_sites,store_site_stats


'''this code re run the analysis for anteater on a given date
it first delete the results for the given date
then re-run and store the results

This is useful to fix when there are problems in importing pcaps, when your 
dns provider fails to deliver, or something happens to ENTRADA.
'''


def delete_data_for_date(dateX):
    print(' Will delete all data for date: ' + str(dateX))
    conn=conn_postgresql()

    tempDate = datetime.strptime(dateX, '%Y%m%d')
    dateY = tempDate + timedelta(days=1)
    dateY = dateY.strftime('%Y%m%d')

    if conn != -1:
        try:
            cur = conn.cursor()

            query = "delete  from anycastsites  where epoch_time >='" + dateX + "' and epoch_time < '" + dateY + "'"
            print(cur.mogrify(query), )
            cur.execute(query)

            query = "delete  from ases   where epoch_time >='" + dateX + "' and epoch_time < '" + dateY + "'"
            print(cur.mogrify(query), (dateX, dateY))
            cur.execute(query)

            query = "delete  from authserver  where epoch_time >='" + dateX + "' and epoch_time < '" + dateY + "'"
            print(cur.mogrify(query), (dateX, dateY))
            cur.execute(query)

            conn.commit()
            conn.close()
            cur.close()

            return 0
        except:
            print("ERROR with deleting old data, no data has been deleted for " + dateX)
            e = sys.exc_info()
            print(str(e))

            #print("ERROR with deleting old data, no data has been deleted for " + dateX)
            return -1
    else:
        print("ERROR with deleting old data, no data has been deleted for " + dateX)
        e = sys.exc_info()
        print(str(e))
        return -1

def makeASqueries(timestampsDict,pars,dateX):
    queryList=[]

    ases = makeASList(pars)

    year=dateX[0:4]
    month=dateX[4:6]
    day=dateX[6:8]


    year = int(year)
    month = int(month)
    day = int(day)

    for k,v in timestampsDict.items():

        # entrada store data in timestamp, so we need to convert these time bins to timestamps
        ts1 =k
        ts2 = v

        entrada_db_table = pars['entrada']['database'] + "." + pars['entrada']['table']

        query = ''' select  asn,server, ipv,  count(1) as nqueries, count(distinct(src)) as resolvers, 
                    count(distinct(server_location)) as nsites, avg(tcp_hs_rtt) as avgRTT  from entrada.dns 
                    where year='''
        query = query + str(year) + " AND  month=" + str(month) + " and  day=" + str(day)
        query = query + " and time between " + str(ts1*1000) + " and " + str(ts2*1000) + " and asn in "

        query = query + ases + " group by asn, server, ipv;"
        #print(query)


        #queryList.append(query)
        key = str(ts1)
        results = runQueryPerAS(query, pars)

        resArray = []
        key = str(ts1)
        for k in results:
            resArray.append(key + "," + k)

        store = store_as_stats(resArray)


def makeSitesQueries(timestampsDict,pars,dateX):
    queryList=[]

    ases = makeASList(pars)

    year=dateX[0:4]
    month=dateX[4:6]
    day=dateX[6:8]


    year = int(year)
    month = int(month)
    day = int(day)

    for k,v in timestampsDict.items():

        # entrada store data in timestamp, so we need to convert these time bins to timestamps
        ts1 =k
        ts2 = v

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

        store = store_site_stats(resArray)


def makeServerQueries(timestampsDict,pars,dateX):
    queryList=[]

    ases = makeASList(pars)

    year=dateX[0:4]
    month=dateX[4:6]
    day=dateX[6:8]


    year = int(year)
    month = int(month)
    day = int(day)

    for k,v in timestampsDict.items():

        # entrada store data in timestamp, so we need to convert these time bins to timestamps
        ts1 =k
        ts2 = v

        entrada_db_table = pars['entrada']['database'] + "." + pars['entrada']['table']

        query = ''' select server,ipv, count(1) as  nqueries, count(distinct(src)) as resolvers,
                   count(distinct(asn)) as asn, avg(tcp_hs_rtt) from '''
        query = query + entrada_db_table + " where year="
        query = query + str(year) + " AND  month=" + str(month) + " and  day=" + str(day)
        query = query + " and time between " + str(ts1 * 1000) + " and " + str(ts2 * 1000) + "  group by server, ipv;"

        results = run_query_per_server(query, pars)
        resArray = []
        key = str(ts1)
        for k, v in results.items():
            resArray.append(key + "," + v)

        store = store_server_stats(resArray)

def makeQueries(dateX):

    year=dateX[0:4]
    month=dateX[4:6]
    day=dateX[6:8]

    #then, create query

    year = int(year)
    month = int(month)
    day = int(day)

    # figure out the timestamps

    # 1. get the date at minight
    input_date = datetime(year=year, month=month, day=day)
    upper_limit_date= input_date+ timedelta(days=1)


    timestamp = calendar.timegm(input_date.utctimetuple())
    hour = int(input_date.strftime("%H"))


    pars=read_ini()
    bin_size = pars['anteater'].getint('size_bins')
    #bin_size=1

    #this is the timestamp dict, which has the intervals
    #for queries
    tsDict=dict()

    numberOfQueries=int(24/(int(bin_size)))

    for i in range (0,numberOfQueries):
        ts1 = timestamp + i*bin_size*3600
        ts2 = timestamp + (i+1)*bin_size*3600

        tsDict[ts1]=ts2

    print("Starting running queries for ASes:")
    ASqueries=makeASqueries(tsDict,pars,dateX)
    print("DONE with queries for ASes")

    print("Starting running queries for Servers:")
    serverQueries=makeServerQueries(tsDict,pars,dateX)
    print("DONE with queries for servers")

    print("Starting running queries for Sites:")
    anycastSitesQuery=makeSitesQueries(tsDict,pars,dateX)
    print("DONE with queries for sites")

def main(date):

    deleteIt = delete_data_for_date(date)
    if deleteIt==0:
        runNew=makeQueries(date)
    else:
        print("failed to delete data\won't re-run queries on ENTRADA. No data updated. ")
    return 0


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  rerun_for_given_date.py $DATE (YYYYMMDD)")


    else:
        run = main(sys.argv[1])
