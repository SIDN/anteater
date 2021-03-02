import json
import impala.dbapi
import sys
import configparser
import string
from datetime import date, timedelta


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
    print("Getting server names from 1 day ago")
    today= today -  timedelta(days = 1)
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    year = int(year)
    month = int(month)
    day = int(day)




    entrada_db_table = pars['entrada']['database'] + "." + pars['entrada']['table']

    entradaQuery = ''' select server,ipv  from '''
    entradaQuery = entradaQuery + entrada_db_table + " where year="
    entradaQuery = entradaQuery + str(year) + " AND  month=" + str(month) + " and  day=" + str(day) +\
                   "  group by server,ipv;"
    cursor = "-1"
    print(entradaQuery)
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
            ipv = str(k[1])
            results.append(server+","+ipv)
    cursor.close()
    conn.close()
    sorted(results)
    print("DEBUG\n results are\n"+ str(results))
    return results

def makeQuery(pars,firstPanel,server_names):

    #targets is a grafana list. each element in a list is a dict that represents a single line in a graph
    #like, graph for ns1.X.com IPv6 queries
    targets=firstPanel['targets']
    #we will store the updated versions here
    newTargetList=[]
    #our demo only has only line, so we copy it here
    demoTS=targets[0]
    alphabet=list(string.ascii_uppercase)



    demoQuery=demoTS['rawSql']
    counter=0
    #now we need to create a new demoTS for each element in k
    # and update the variables accordingly
    for k in server_names:
        sp=k.split("-")
        demoTS = targets[0]
        tempTS = demoTS.copy()
        demoQuery = demoTS['rawSql']
        tempServer=sp[0].strip()
        ipv=sp[1].strip()
        if '4' in ipv:
            ipv=4
        elif '6' in ipv:
            ipv=6
        label=k

        copyDemoTS=demoTS
        #tempSQL=singleLine['rawSql']
        #print(tempSQL)
        newQuery=demoQuery.replace("$LABEL", label)
        #print(tempSQL)
        newQuery=newQuery.replace("$SERVER_NAME", tempServer)
        newQuery=newQuery.replace("$IPV",str(ipv))
        tempTS['rawSql']=newQuery
        #each line has its own id, alphabet sequence, so we need to get it
        tempTS['refId']=alphabet[counter]
        counter=counter+1
        newTargetList.append(tempTS)

    firstPanel['targets'] = newTargetList

    return firstPanel



def main():

    pars=read_ini()

    server_names = get_server_names(pars)


    baseJSON=''
    with open('templates/authservers.json') as f:

        baseJSON=json.load(f)

    firstPanel=baseJSON['panels'][0]
    tempPanel=makeQuery(pars,firstPanel,server_names)
    baseJSON['panels'][0]=tempPanel

    #second panel
    secondPanel=baseJSON['panels'][1]
    tempPanel = makeQuery(pars, secondPanel, server_names)
    baseJSON['panels'][1]=tempPanel

    thirdPanel=baseJSON['panels'][2]
    tempPanel = makeQuery(pars, thirdPanel, server_names)
    baseJSON['panels'][2]=tempPanel

    lastPanel=baseJSON['panels'][3]
    tempPanel = makeQuery(pars, lastPanel, server_names)
    baseJSON['panels'][3]=tempPanel


    with open('yourDashboards/authservers.json', 'w') as f:
        json.dump(baseJSON,f)
    print("Dashboard generated. Import tourDashboards/authservers.json into Grafana and enjoy!")


if __name__ == "__main__":

    if len(sys.argv) != 1:
        print("Wrong number of parameters\n")
        print(str(len(sys.argv)))
        print("Usage:  python dashboard-auth-servers.py")


    else:


        z=main()

