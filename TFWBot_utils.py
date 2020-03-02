from TFWBot_enums import *
import ast
import random
class TFWBot_Session():
    def __init__(self,user_id,state,time,data):
        self.user_id = user_id
        self.state = state
        self.time = time
        self.data = data
        
    def __str__(self):
        return str(self.__dict__)
class ActionCommandObject(): 
    def __init__(self,object_id,group_id=-1):
        self.actions = {}
        self.replies = {}
        self.object_id = object_id
        self.group_id = group_id
    def load_from_db(self,db_object):
        _db_object = db_object
        if(len(_db_object) == 1):
            _db_object = _db_object[0]
        print(_db_object)
        name, group_id, actions, replies = _db_object
        self.object_id = name
        self.group_id = int(group_id)
        self.actions = self.db_to_message(actions)
        self.replies = self.db_to_message(replies)
        # print(name, group_id, actions, replies)
        # print(self.object_id,self.group_id,self.actions,self.replies)
    def db_to_message(self,load_list):
        _load_list = load_list
        store_dict = {}
        if(isinstance(load_list,str)):
            _load_list = ast.literal_eval(_load_list)
        for val in _load_list:
            msg_type_db, true_val= val.split(":::")
            msg_type = self.db_to_message_type(msg_type_db)
            tmp = (true_val,msg_type)
            store_dict[str(tmp)] = tmp
            print(tmp)
        return store_dict
    def db_to_message_type(self,db_message):
        if("t" == db_message):
            return message_types.TEXT
        elif("st" == db_message):
            return message_types.STICKER
        elif("gif" == db_message):
            return message_types.GIF
        return message_types.UNKNOWN
    def message_type_to_db(self,message_type):
        _mt = message_type
        if(isinstance(message_type,tuple)):
            _mt = _mt[1]
        if(_mt == message_types.TEXT):
            return "t"
        if(_mt == message_types.STICKER):
            return "st"
        if(_mt == message_types.GIF):
            return "gif"
        return None
    def make_db_object(self):
        group_id = self.group_id
        if(group_id is None):
            group_id = -1
        actions = []
        replies = []
        for k in self.actions:
            action = self.actions[k]
            ah = self.message_type_to_db(action)
            if(ah is not None):
                actions.append(str(ah)+":::"+action[0])
        for k in self.replies:
            reply = self.replies[k]
            rh = self.message_type_to_db(reply)
            if(rh is not None):
                replies.append(str(rh)+":::"+reply[0])
        return self.object_id,group_id, actions, replies
    def add_action(self,action,action_type = message_types.TEXT):
        tmp = (action,action_type)
        self.actions[str(tmp)] = tmp
    def add_reply(self,reply,reply_type = message_types.TEXT):
        tmp = (reply,reply_type)
        self.replies[str(tmp)] = tmp
    def remove_action(self,action,action_type = message_types.TEXT):
        tmp = str((action,action_type))
        if(tmp in self.actions):
            del self.actions[tmp]

       
    def remove_reply(self,reply,reply_type = message_types.TEXT,bot = None):
        if(reply_type == message_types.STICKER):
            rep_file = bot.get_file(reply)
            exist_file = None
            for k in self.replies:
                rep = self.replies[k]
                #print(rep)
                if(rep[1] == message_types.STICKER):
                    exist_file = bot.get_file(rep[0])
                    if(exist_file.file_path == rep_file.file_path):
                        del self.replies[k]
                        return True
        elif(reply_type == message_types.GIF):
            rep_file = bot.get_file(reply)
            exist_file = None
            for k in self.replies:
                rep = self.replies[k]
                #print(rep)
                if(rep[1] == message_types.GIF):
                    exist_file = bot.get_file(rep[0])
                    if(exist_file.file_path == rep_file.file_path):
                        del self.replies[k]
                        return True

        else:
            tmp = str((reply,reply_type))
            if(tmp in self.replies):
                del self.replies[tmp]
                return True
        return False
    def __str__(self):
        return str((self.object_id,self.group_id,self.actions,self.replies))

class ActionCommandController():
    def __init__(self,db_data):
        self.actions_text = {}
        self.actions_sticker = {}
        self.load(db_data)
        
    def load(self,db_data):
        self.actions_text = {}
        self.actions_sticker = {}
        for i in db_data:
            tmp = ActionCommandObject(0)
            tmp.load_from_db(i)
            tmp_replies = []
            for k in tmp.replies:
                v = tmp.replies[k]
                tmp_replies.append(v)
            for k in tmp.actions:
                v = tmp.actions[k]
                if(v[1] == message_types.STICKER):
                    if(str(v[0]) in self.actions_sticker):
                        print(str(v[0]))
                        self.actions_sticker[str(v[0])].extend(tmp_replies)
                    else:
                        self.actions_sticker[str(v[0])] = tmp_replies
                elif(v[1] == message_types.TEXT):
                    if(str(v[0]) in self.actions_text):
                        self.actions_text[str(v[0])].extend(tmp_replies)
                    else:
                        self.actions_text[str(v[0])] = tmp_replies
        print(self.actions_text,self.actions_sticker)
    def grab_reply(self,options):
        return random.choice(options)
    def check_list(self,action_list,message_list):
        _action_list = action_list
        _message_list = message_list
        if(isinstance(_message_list,str)):
            _message_list = _message_list.replace(",","").replace(".","").split(" ")
        if(isinstance(_action_list,str)):
            _action_list = _action_list.replace(",","").replace(".","").split(" ")
        ret = False
        ind = 0
        # print("DEBUG")
        # print(message_list,_message_list)
        # print(action_list,_action_list)
        for i in _message_list:
            #print(i,  _action_list[ind],ind, len(_action_list))
            if(i == _action_list[ind]):
                ind += 1
            if(ind >= len(_action_list)):
                ret = True
        return ret
    def run(self,msg_msg_type_pair,update,context):
        message, message_type = msg_msg_type_pair
        reply = None
        print(message)
        if(message_type == message_types.STICKER):
            if(str(message) in self.actions_sticker):
                reply = self.grab_reply(self.actions_sticker[str(message)])
        if(message_type == message_types.TEXT):
            for action in self.actions_text:
                if(self.check_list(action,message)):
                    reply = self.grab_reply(self.actions_text[action])
                    break
        if(reply is not None):
            #print(reply)
            if(reply[1] == message_types.STICKER):
                update.message.reply_sticker(reply[0],quote=True)
            elif(reply[1] == message_types.TEXT):
                update.message.reply_text(reply[0],quote=True)
            elif(reply[1] == message_types.GIF):
                update.message.reply_animation(reply[0],quote=True)


