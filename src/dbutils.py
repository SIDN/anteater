import impala.dbapi
from impala.dbapi import connect
import calendar
import psycopg2
import logging
import sys

def conn_impala(server1,port1,ssl1,auth1):
    try:
        return impala.dbapi.connect(host=server1, port=port1, use_ssl=ssl1,auth_mechanism=auth1)
    except:
        e = sys.exc_info()
        print("Error in conn_impala: " + str(e))


