from _common.utils.db import MongoDB
from _common.utils.conn import Server
import time
import threading
def mongo_query():
    mongo_db = MongoDB()
    mongo_coll = mongo_db['test']
    mongo_coll.insert_many([{ 'a': 2 }, { 'b': 5 }])

def do_something(msg):
    print('Consultado Base de datos')
    x = threading.Thread(target=mongo_query)
    x.start()
    x.join()
    print('Hecha la consulta')
# x = threading.Thread(target=do_something)
# x.start()
# x.join()
ctrl_server = Server('Control', '127.0.0.1', 60011,
                             do_something)
ctrl_server.start()
print('Servidor iniciado')
while True:
    pass
