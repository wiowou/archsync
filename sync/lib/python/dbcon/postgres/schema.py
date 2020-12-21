from .table import Table
from .routine import Routine
from psycopg2 import connect

class Schema:
    def __init__(self, sch_name, user_name, host_name=None):
        self.sch_name = sch_name
        self.user_name = user_name
        self.host_name = host_name
        self.tables = {}
        self.conn = None #psycopg2 connection class
        self.refresh()
    
    def refresh(self):
        conn_str = 'dbname=' + self.sch_name + ' user=' + self.user_name
        if not self.host_name is None:
            conn_str += ' host=' + self.host_name
        self.conn = connect(conn_str)
        q = "select table_name from information_schema.tables where table_catalog = '" + self.sch_name + "' and table_schema = 'public'"
        qr = "select distinct routine_name from information_schema.routines where specific_catalog = '" + self.sch_name + "' and routine_schema = 'public'"
        cur = self.conn.cursor()
        try:
            cur.execute(q)
            tab_names = cur.fetchall()
            for tn in tab_names:
                tab_name = tn[0]
                self.tables[tab_name] = Table(self.conn, tab_name)
            cur.execute(qr)
            rtn_names = cur.fetchall()
            for rn in rtn_names:
                rtn_name = rn[0]
                tbl = None
                if 'v' + rtn_name[1:] in self.tables:
                    tbl = self.tables['v' + rtn_name[1:]]
                self.tables[rtn_name] = Routine(self.conn, rtn_name, tbl)
        except:
            raise
        finally:
            cur.close()
    
    def __getitem__(self, key):
        return self.tables[key]
    
    def __del__(self):
        self.conn.close()