class Routine:
    def __init__(self, conn, rtn_name, table=None):
        self.conn = conn
        self._table = table
        self.rtn_name = rtn_name
        self._tab_name = None

        if not self._table is None:
            self._table.tab_name = self.rtn_name
    
    def __call__(self, *args):
        self._set_tab_name(*args)
        if self._table is None:
            return
        self._table.tab_name = self._tab_name 
        return self
    
    def _set_tab_name(self, *args):
        if len(args) == 0:
            self._tab_name = self.rtn_name + '()'
            return
        self._tab_name = self.rtn_name + '(' + str(args[0])
        for a in args[1:]:
            self._tab_name += ',' + str(a)
        self._tab_name += ')'

    def select(self, col_names='*', conditions=None):
        if self._table is None:
            conn = self.conn
            q = 'select * from ' + self._tab_name
            cur = conn.cursor()
            try:
                cur.execute(q)
                rows = cur.fetchall()
                if len(rows[0]) == 1:
                    return rows[0][0]
                else:
                    return rows[0]
            except:
                raise
            finally:
                cur.close()
        self._table.select(col_names, conditions)
    
    def __getitem__(self, key):
        return self._table.columns[key]