class Column:
    def __init__(self, pg_type, optional=True, is_pk=False, is_fk=False, length=None):
        self.length = length
        self.pg_type = pg_type
        self.optional = optional
        self.is_pk = is_pk
        self.is_fk = is_fk
        self.values = []
    
    def __getitem__(self, key):
        return self.values[key]
    
    def __setitem__(self, key, value):
        self.values[key] = value
    
    def __len__(self):
        return len(self.values)
