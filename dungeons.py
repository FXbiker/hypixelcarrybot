import json

class DungeonsCarry:
    def __init__ (self, db_filename):
        #, 'M2', 'M3', 'M4', 'M5', 'M6', 'M7'
        self.codes = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'M1']
        carrydb = {x: [] for x in self.codes}
        self.db_filename = db_filename
        with open(f'{self.db_filename}.json') as f:
            f = json.load(f)
            for x in self.codes:
                if x in f:
                    pass
                else:
                    f[x] = []
        with open(f'{self.db_filename}.json', 'w') as fi:
            json.dump(f, fi)
    def database_get(self):
        with open(f'{self.db_filename}.json') as f:
            out = json.load(f)
            f.close()
            return out
    def database_update(self, database):
        with open(f'{self.db_filename}.json', 'w') as outfile:
            json.dump(database, outfile)
            outfile.close()

    def request_carry(self, floor, uid):
        db=self.database_get()
        db[floor.upper()].append(uid)
        self.database_update(db)

    def cancel_carry(self, uid):
        db=self.database_get()
        for x in db:
            for i in db[x]:
                if i == uid:
                    db[x].remove(uid)
        self.database_update(db)

    def start_carry(self, ppl, floor):
        db = self.database_get()
        if (len(db[floor.upper()]) // ppl) >= 1:
            pass
        else:
            ppl = len(db[floor.upper()]) % ppl
        ids = []
        print(db)
        for x in range(ppl):
            id = db[floor.upper()].pop(x)
            ids.append(int(id))
        self.database_update(db)
        return ids

    def check_active_carry(self, uid):
        db = self.database_get()
        for x in db:
            if uid in db[x]:
                return True
        return False