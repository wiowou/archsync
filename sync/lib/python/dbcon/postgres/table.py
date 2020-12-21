from .column import Column
from psycopg2 import extras

class Table:
    def __init__(self, conn, tab_name):
        self.conn = conn
        self.tab_name = tab_name
        self.columns = {}
        #self.last_id = None #int
        self.mandatory_cols = None #dict

        cur = conn.cursor()
        q = """select column_name, is_nullable, data_type, character_maximum_length 
        from information_schema.columns where table_name = '"""
        q += self.tab_name + "'"
        con_q = """select kcu.column_name, tc.constraint_type from information_schema.key_column_usage as kcu  
        inner join information_schema.table_constraints as tc  
        on tc.constraint_name = kcu.constraint_name   
        where tc.table_name = '"""
        con_q += self.tab_name + "'"
        try:
            cur.execute(con_q)
            col_keys = cur.fetchall()
            constraints = {}
            for ck in col_keys:
                constraints[ck[0]] = ck[1]
            cur.execute(q)
            col_attrs = cur.fetchall()
            for ca in col_attrs:
                col_name = ca[0]
                col_type = ca[2]
                col_len = ca[3]
                if not col_len is None:
                    col_len = int(col_len)
                is_pk = col_name in constraints and constraints[col_name] == 'PRIMARY KEY'
                is_fk = col_name in constraints and constraints[col_name] == 'FOREIGN KEY'
                optional = ca[1] == 'YES' or is_pk
                self.columns[col_name] = Column(col_type, optional, is_pk, is_fk, col_len)
            self.mandatory_cols = set([k for k,v in self.columns.items() if not v.optional])
        except:
            raise
        finally:
            cur.close()
        #self._get_last_id()

    def last_id(self):
        conn = self.conn
        seq_q = 'select max(id) from '
        seq_q += self.tab_name
        cur = conn.cursor()
        try:
            cur.execute(seq_q)
            last_id = cur.fetchall()
            ret = last_id[0][0]
            if ret == 1:
                count_q = 'select count(*) from "' + self.tab_name + '"'
                cur.execute(count_q)
                length = cur.fetchall()
                length = length[0][0]
                ret = min(self.last_id, length)
        except:
            conn.reset()
        finally:
            cur.close()
        return ret
    
    def delete(self, conditions=None):
        conn = self.conn
        cur = conn.cursor()
        q = 'delete from "' + self.tab_name + '"'
        if not conditions is None:
            q += ' where ' + conditions
        try:
            cur.execute(q)
            conn.commit()
        except:
            raise
        finally:
            cur.close()
    
    def insert(self, col_names, rows):
        conn = self.conn
        cur = conn.cursor()
        q = 'insert into "' + self.tab_name + '" ('
        q += '"' + col_names[0] + '"'
        for cn in col_names[1:]:
            q += ', "' + cn + '"'
        q += ') values %s'
        try:
            extras.execute_values(cur, q, rows)
            conn.commit()
        except:
            raise
        finally:
            cur.close()
        #self._get_last_id()
    
    def update(self, col_names, rows):
        conn = self.conn
        cur = conn.cursor()
        q = 'update "' + self.tab_name + '" set '
        q += '"' + col_names[0] + '" = d."' + col_names[0] + '"'
        for cn in col_names[1:]:
            q += ', "' + cn + '" = d."' + cn + '"'
        q += ' from (values %s) as d ('
        q += '"' + col_names[0] + '"'
        for cn in col_names[1:]:
            q += ', "' + cn + '"'
        pks = [cn for cn,c in self.columns.items() if c.is_pk]
        q += ') where d."' +  pks[0] + '" = "' + self.tab_name + '"."' +  pks[0] + '"'
        for pk in pks[1:]:
            q += ' and "' +  pk + '" = "' + self.tab_name + '"."' +  pk + '"'
        try:
            extras.execute_values(cur, q, rows)
            conn.commit()
        except:
            raise
        finally:
            cur.close()

    def select(self, col_names='*', conditions=None):
        conn = self.conn
        if col_names == '*':
            col_names = list(self.columns.keys())
        cur = conn.cursor()
        q = 'select "' + col_names[0] + '"'
        for cn in col_names[1:]:
            q += ', "' + cn + '"'
        q += ' from ' + self.tab_name 
        if not conditions is None:
            q += ' where ' + conditions
        for cn in self.columns.keys():
            self.columns[cn].values = []
        try:
            cur.execute(q)
            rows = cur.fetchall()
            for r in rows:
                for i in range(len(col_names)):
                    self.columns[col_names[i]].values.append(r[i])
        except:
            raise
        finally:
            cur.close()

    def check_insert(self, col_names, rows):
        s_col_names = set(col_names)
        missing_cols = self.mandatory_cols - s_col_names
        if len(missing_cols) > 0:
            raise Exception('missing mandatory columns')
        if len(rows) == 0:
            raise Exception('need at least 1 row')
        if not len(rows[0]) == len(col_names):
            raise Exception('number of col_names must equal row length')

    def check_col_names(self, col_names):
        s_col_names = set(col_names)
        existant = set(self.columns.keys())
        non_existant = s_col_names - existant
        if len(non_existant) > 0:
            raise Exception('column names are not in table')
    
    def __getitem__(self, key):
        return self.columns[key]
    
    def __len__(self):
        if len(self.columns) == 0:
            return 0
        for col_name in self.columns.keys():
            return len(self.columns[col_name].values)

