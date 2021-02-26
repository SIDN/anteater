import configparser
from dbutils import conn_impala

cfg=configparser.ConfigParser()
cfg.read('anteater-debug.ini')

server=cfg['impala']['server']
port=cfg['impala'].getint('port')
ssl=cfg['impala'].getboolean('use_ssl')
auth=cfg['impala']['auth_mechanism']

conn=conn_impala(server,port,ssl,auth)

print(str(conn))

conn.close()
print(str(conn))