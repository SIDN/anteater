import impala.dbapi
from impala.dbapi import connect
import calendar
import psycopg2
import logging
import sys
import configparser

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


def conn_postgresql():
    pars=read_ini()
    host1=pars['postgresql']['server']
    database1=pars['postgresql']['database']
    port1=pars['postgresql'].getint('port')
    user1=pars['postgresql']['username']
    password1=pars['postgresql']['password']


    try:
        conn = psycopg2.connect(host=host1, database=database1, port=port1, user=user1,
                                password=password1)
        return conn
    except:
        e = sys.exc_info()
        print("Error in conn_postgresql: " + str(e))

def read_ini():
    cfg = configparser.ConfigParser()
    cfg.read('anteater.ini')
    return cfg