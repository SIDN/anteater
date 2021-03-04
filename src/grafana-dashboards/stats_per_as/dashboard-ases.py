import json
import impala.dbapi
import sys
import configparser
import string
from datetime import date, timedelta
import string
import random


def id_generator(size=9, chars=string.ascii_uppercase + string.digits + string.ascii_lowercase):
     return ''.join(random.choice(chars) for _ in range(size))


def conn_impala():
    pars=read_ini()
    server1=pars['impala']['server']
    port1=pars['impala'].getint('port')
    use_ssl1=pars['impala']['use_ssl']
    auth_mechanism1=pars['impala']['auth_mechanism']

    try:
        return impala.dbapi.connect(host=server1, port=port1, use_ssl=use_ssl1,auth_mechanism=auth_mechanism1)
    except:
        e = sys.exc_info()
        print("Error in conn_impala: " + str(e))




def read_ini():
    cfg = configparser.ConfigParser()
    cfg.read('../../anteater.ini')
    return cfg

def get_server_names(pars):


    today = date.today()
    print("Getting server names from 2 days ago")
    today= today -  timedelta(days = 2)
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    year = int(year)
    month = int(month)
    day = int(day)




    entrada_db_table = pars['entrada']['database'] + "." + pars['entrada']['table']

    entradaQuery = ''' select server  from '''
    entradaQuery = entradaQuery + entrada_db_table + " where year="
    entradaQuery = entradaQuery + str(year) + " AND  month=" + str(month) + " and  day=" + str(day) +\
                   "  group by server;"
    cursor = "-1"

    conn = conn_impala()

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
            print('entradaQuery')
            cursor.execute(entradaQuery, configuration={"REQUEST_POOL": pool})
        else:
            cursor.execute(entradaQuery)
    except:
        print("error executing")
        e = sys.exc_info()
        print(str(e))
        cursor.close()

    # parse results
    results  =[]
    if cursor != 1:

        print('start to retrieve row  of cursor')
        # select server,ipv, count(1) as  nqueries,avg(tcp_hs_rtt) from
        for k in cursor:
            server = str(k[0])
            results.append(server)
    cursor.close()
    conn.close()
    sorted(results)
    #print("DEBUG\n results are\n"+ str(results))
    return results


def makeQuery(pars,firstPanel,serverList,dictASes,ipv):

    #targets is a grafana list. each element in a list is a dict that represents a single line in a graph
    #like, graph for ns1.X.com IPv6 queries
    targets=firstPanel['targets']
    #we will store the updated versions here
    newTargetList=[]
    #our demo only has only line, so we copy it here
    demoTS=targets[0]
    alphabet=list(string.ascii_uppercase)


    pg_db = pars['postgresql']['database']
    demoQuery=demoTS['rawSql']
    counter=0
    secondCounter=1

    demoTS = targets[0]

    #       panelList.append(makeQuery(pars, queriesPanel,serverList, dictASes,4))

    setServers=set(serverList)
    servers=list(setServers)
    servers.sort()

    #now we need to create a new demoTS for each element in k
    # and update the variables accordingly
    for singleServer in servers:
        if singleServer!='':
            for singleAS in dictASes.keys():
                tempTS = demoTS.copy()
                demoQuery = demoTS['rawSql']
                label=dictASes[singleAS]+"-"+ singleAS +"-"+ singleServer

                newQuery=demoQuery.replace("$LABEL", label)

                newQuery=newQuery.replace("$SERVER_NAME", singleServer)
                newQuery=newQuery.replace("$IPV",str(ipv))
                newQuery = newQuery.replace("$AS_NAME", str(dictASes[singleAS]))
                newQuery = newQuery.replace("$AS_NUMBER", str(singleAS))
                tempTS['rawSql']=newQuery
                #each line has its own id, alphabet sequence, so we need to get it
                if counter<26:
                    tempTS['refId']=alphabet[counter]
                else:
                    tempTS['refId']="A"+ str(secondCounter)
                    secondCounter=secondCounter+1
                counter=counter+1
                #print(tempTS['rawSql'])
                newTargetList.append(tempTS)

    firstPanel['targets'] = newTargetList
    #print(str(newTargetList))
    pg_db='debug'
    firstPanel['datasource']=pg_db
    firstPanel['title'] = firstPanel['title'].replace("$IPV", "IPv"+str(ipv))

    return firstPanel

def makeServerPanels(serverList,pars):


    #first, let's create a dict with the ASes in question:
    monitoredASes=pars['anteater']['ases_to_monitor']
    sp=monitoredASes.split(",")
    dictASes=dict()
    #15169-Google, 8075-Microsoft, 16509-AWS, 14618-AWS,  32934-Facebook, 36692-OpenDNS, 13335-Cloudflare
    for k in sp:
        sp=k.split("-")
        tempASN=sp[0].strip()
        tempASNname=sp[1]
        dictASes[tempASN]=tempASNname



    baseJSON=''
    with open('template/template.json') as f:
        baseJSON = json.load(f)
        copyBaseJSON=baseJSON.copy()
        localPanel=baseJSON.copy()

        # extract all panels before adding stuff
        queriesPanel = copyBaseJSON['panels'][0]
        queriesPanelV6 = copyBaseJSON['panels'][1]

        rttPanel = copyBaseJSON['panels'][2]
        rttPanelV6 = copyBaseJSON['panels'][3]

        sitesPanel = copyBaseJSON['panels'][4]
        sitesPanelV6 = copyBaseJSON['panels'][5]

        resolversPanel = copyBaseJSON['panels'][6]
        resolversPanelV6 = copyBaseJSON['panels'][7]

        # nee to generate one query per AS and server

        panelList=[]
        panelList.append(makeQuery(pars, queriesPanel,serverList, dictASes,4))
        panelList.append(makeQuery(pars, queriesPanelV6, serverList, dictASes, 6))

        #rtt
        panelList.append(makeQuery(pars, rttPanel,serverList, dictASes,4))
        panelList.append(makeQuery(pars, rttPanelV6, serverList, dictASes, 6))


        #sites
        panelList.append(makeQuery(pars, sitesPanel, serverList, dictASes, 4))
        panelList.append(makeQuery(pars, sitesPanelV6,serverList, dictASes, 6))
        # resolvers
        panelList.append(makeQuery(pars, resolversPanel, serverList, dictASes,4))
        panelList.append(makeQuery(pars, resolversPanelV6, serverList, dictASes, 6))



        localPanel['panels'] = panelList
        localPanel['uid']= id_generator()

        with open('export/ases.json', 'w') as aus:
            #print(str(baseJSON))
            json.dump(localPanel,aus)
            aus.close()
        print("Dashboard generated. Import export/ases.json into Grafana and enjoy it !")


def main():

    pars=read_ini()
    #list with sever_name,ipv
    server_names = get_server_names(pars)

    jsonFile=makeServerPanels(server_names,pars)


if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  python dashboard-auth-servers.py")
    else:

        z=main()