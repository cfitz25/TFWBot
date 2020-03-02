import sqlite3
import logging
import ast
import TFWBot_utils
import TFWBot_enums
class TFWDBWrapper():
    def __init__(self,db_name,reset=True):
        self.conn = sqlite3.connect(db_name+".db",check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.db_name = db_name
        self.def_names()
        ret = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;",(self.ACTION_COMMAND_TABLE,))
        data = ret.fetchall()
        if(len(data) == 0 or reset):
            self.reset_db()
    def reset_db(self):
        build_command = "CREATE TABLE "
        build_command += self.ACTION_COMMAND_TABLE + " ("
        cols = [(self.ACTION_COMMAND_ID,"text"),
                (self.GROUP_COL,"integer"),
                (self.ACTION_COL,"text"),
                (self.REPLY_COL,"text")]
        for col in cols:
            build_command += col[0] + " " + col[1] + ", "
        build_command += "PRIMARY KEY("+self.ACTION_COMMAND_ID+"))"
        print(build_command)
        try:
            ret = self.cursor.execute(build_command)
            data = ret.fetchall()
            print(data)
        except Exception as e:
            print(e)
            ret = self.cursor.execute("DROP TABLE "+self.ACTION_COMMAND_TABLE)
            print(ret)
            ret = self.cursor.execute(build_command)
            data = ret.fetchall()
            print(data)
        self.conn.commit()
        
    def def_names(self):
        self.ACTION_COMMAND_TABLE = "sticker_reply_table"
        self.ACTION_COMMAND_ID = "action_command_id"
        self.GROUP_COL = "group_id"
        self.ACTION_COL = "action_col"
        self.REPLY_COL = "reply_col" 
        self.ACTION_COMMAND_COLS = (self.ACTION_COMMAND_ID,self.GROUP_COL,self.ACTION_COL,self.REPLY_COL)
    def get(self,table,tag,tag_value):
        build_command = "SELECT * FROM "+str(table)
        if(tag_value is None):
            build_command += ";"
        else:
            build_command += " WHERE " +str(tag) + '="' +str(tag_value)+'";'
        ret = self.cursor.execute(build_command).fetchall()
        return ret
    def insert(self,table,columns,data,overwrite=False):
        if(len(columns) != len(data)):
            return False
        build_command = "INSERT "
        if(overwrite):
            build_command += "OR REPLACE "
        build_command +=  "INTO "+str(table)+"("
        for i in columns:
            build_command += str(i) + ","
        build_command = build_command[:-1] + ") VALUES("
        for i in data:
            build_command += "?,"
        build_command = build_command[:-1] + ");"
        # print("INSERT",build_command)
        # print("INSERT",data)
        try:
            ret = self.cursor.execute(build_command,data)
            self.conn.commit()
            return True
        except Exception as e:
            logging.error(e,exc_info=True)
            return False
        
    def exists(self,table,tag,tag_value):
        build_command = "SELECT EXISTS(SELECT 1 FROM "+str(table) + " WHERE " +str(tag) + '="' +str(tag_value)+'");'
        ret = self.cursor.execute(build_command)
        data = ret.fetchone()
        return True if data[0] == 1 else False
    def delete(self,table,tag,tag_value):
        build_command = "DELETE FROM "+str(table) + " WHERE " +str(tag) + '="' +str(tag_value)+'";'
        ret = self.cursor.execute(build_command)
        self.conn.commit()
        return True#True if data[0] == 1 else False
    def check_action_command_name_exists(self,name):
        ret = self.exists(self.ACTION_COMMAND_TABLE,self.ACTION_COMMAND_ID,name)
        return ret
    def load_action_command(self,name):
        ret = self.get(self.ACTION_COMMAND_TABLE,self.ACTION_COMMAND_ID,name)
        return ret
    def save_action_command(self,name,data):
        _data = []
        for d in data:
            _data.append(str(d))
        ret = self.insert(self.ACTION_COMMAND_TABLE,self.ACTION_COMMAND_COLS,_data,overwrite=True)
        return ret
    def remove_action_command(self,name):
        ret = self.delete(self.ACTION_COMMAND_TABLE,self.ACTION_COMMAND_ID,name)
        return ret
if __name__ == '__main__':

    test = TFWDBWrapper("test")
    print(test.check_action_command_name_exists("t"))
    print(test.load_action_command("t"))
    #data = ast.literal_eval("(-1, ['st:CAACAgIAAxkBAAIBgl4rtcUv4W4_n3IGHlGjOkVSB2h7AAKNAANgH_oKO01adTFd0QUYBA', 'st:CAACAgIAAxkBAAIBg14rtcUEky2Of3R_DxnIJr_G1-XPAAICAANlbZgfFS2a7hoi0YQYBA', 'st:CAACAgQAAxkBAAIBhV4rtcbuZc4NwIWJ5-C8qBmdRSGlAAKeAgACcxpEBWEKqq2ruXwZGAQ'], ['st:CAACAgIAAxkBAAIBjV4rtcvsFIyXIS9q8dJEhJkriv9xAAIKAQACYB_6ClPa63qBbMc5GAQ', 'st:CAACAgIAAxkBAAIBjl4rtct9mfC3CqTRbtZWa7CXQhGNAALBAANgH_oKefJ2Iv8LQXcYBA', 'st:CAACAgQAAxkBAAIBj14rtczHbHt5CMuA2Af-7Ks6NG1qAAL5AgACDMiNBZPBTJ7zJSNuGAQ'])")
    name = "l"
    sess = TFWBot_utils.ActionCommandObject(name)
    sess.add_action("STICK_ACT",TFWBot_enums.message_types.STICKER)
    sess.add_action("TEXT_ACT",TFWBot_enums.message_types.TEXT)
    sess.add_reply("STICK_REP",TFWBot_enums.message_types.STICKER)
    sess.add_reply("TEXT_REP",TFWBot_enums.message_types.TEXT)
    data = sess.make_db_object()
    #print(data)
    
    #data = [name] + list(data)
    print(test.save_action_command(name,data))
    print(test.save_action_command(name,data))
    load_data = test.load_action_command(name)
    sess2 = TFWBot_utils.ActionCommandObject(name)
    sess2.load_from_db(load_data)
    print(sess)
    print(sess2)
    