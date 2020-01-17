import sqlite3

class TFWDBWrapper():
    def __init__(self,db_name,reset=True):
        self.conn = sqlite3.connect(db_name+".db")
        self.cursor = self.conn.cursor()
        self.db_name = db_name
        self.def_names()
        ret = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;",(self.MAIN_TABLE,))
        data = ret.fetchall()
        if(len(data) == 0 or reset):
            self.reset_db()
    def reset_db(self):
        build_command = "CREATE TABLE "
        build_command += self.MAIN_TABLE + " ("
        cols = [(self.GROUP_COL,"text"),
                (self.TRIGGERS_COL,"text"),
                (self.REPLY_COL,"text")]
        for col in cols:
            build_command += col[0] + " " + col[1] + ", "
        build_command = build_command[:-2] + ")"
        try:
            ret = self.cursor.execute(build_command)
            data = ret.fetchall()
            print(data)
        except Exception as e:
            print(e)
        
    def def_names(self):
        self.MAIN_TABLE = "main_table"
        self.GROUP_COL = "group_id"
        self.TRIGGERS_COL = "triggers_col"
        self.REPLY_COL = "feel_col"

if __name__ == '__main__':
    test = TFWDBWrapper("test")