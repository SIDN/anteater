import impala.dbapi
from impala.dbapi import connect
import calendar
import psycopg2
import logging
import sys

def conn_impala(server,port,ssl,auth):
    conn=''
    try:
        return impala.dbapi.connect(host=server, port=port, use_ssl=ssl,auth_mechanism=auth)
    except:
        e = sys.exc_info()[0]
        print("Error in connectImpala: " + str(e))


