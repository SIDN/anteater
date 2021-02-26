import configparser
from dbutils import conn_impala

cfg=configparser.ConfigParser()
cfg.read('anteater-debug.ini')

server=cfg['impala'].getstring['server']
print(server)
port=cfg['impala'].getint('port')
print(port)
ssl=cfg['impala'].getboolean('use_ssl')
print(ssl)
auth=cfg['impala'].getstring['auth_mechanism']
print(auth)
conn=conn_impala(server,port,ssl,auth)

print(str(conn))

conn.close()
print(str(conn))