#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import traceback
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import time
from TFWBot_enums import *
from TFWBot_utils import *
from TFWBotDB import *
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
# CAACAgIAAxkBAAICZF4r1NrbO1Ks_Y01u99uiWLVd4rDAAKNAANgH_oKO01adTFd0QUYBA
# CAACAgIAAxkBAAICbl4r1TN1xDnkrWs5GTUitlwTok3nAAKNAANgH_oKO01adTFd0QUYBA
# AAMCAgADGQEAAgJuXivVM3XEOeStazkZNSK2XBOiTecAAo0AA2Af-go7TVp1MV3RBRoeSw0ABAEAB20AA3dgAQABGAQ
groups = {}
wait_time_s = float(10*60)
new_group = [0,wait_time_s,False,0]
god_users = [904522230]

session = {}
db = TFWDBWrapper("TFWBotv2",reset=False)

def load_all_action_command(db):
    ret = db.load_action_command(None)
    return ret

all_actions = load_all_action_command(db)
actions_command_controller = ActionCommandController(all_actions)

def make_session(user_id,state,data):
    _time = time.time()
    return TFWBot_Session(user_id=user_id,state=state,time=_time,data=data)
def new_session(user_id,state,data):
    global session
    sess = make_session(user_id,state,data)
    session[sess.user_id] = sess
def session_timeout():
    global session
    _time = time.time()
    
    # for k in session:
    #     s = session[k]
    #     if(_time - s.time > 100):
    #         remove_session(s)

def check_sessions(user_id):
    global session
    session_timeout()
    _user_sess = None
    if(user_id in session):
        _user_sess = session[user_id]
        print(_user_sess)
    #print(_user_sess,session,user_id)
    return _user_sess
def remove_session(sess):
    global session
    print(session[sess.user_id])
    del session[sess.user_id]
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    print(update)
    update.message.reply_text('Hi!')
    print(context.bot.get_me())
def reload_actions_controller(update,context):
    global actions_command_controller
    global db
    ret = load_all_action_command(db)
    actions_command_controller.load(ret)
    update.message.reply_text("Ready to yeet cunts into orbit.")
def new_action_reply_command(update,context):
    global session
    user_id = update.message.from_user.id
    data = None
    sess = new_session(user_id,state_create_reply.BEGIN,data)
    update.message.reply_text("Enter name for command (will load existing if it.. well exists)")
def print_actions_command(update,context):
    global db
    try:
        ret = load_all_action_command(db)
        print(ret)
        ret_str = "All Actions IDs: \r\n"
        for i in ret:
            ret_str += str(i[0]) + "\r\n"
        update.message.reply_text(ret_str)
    except Exception as e:
        logging.error(e)#,exc_info=True)
def create_reply_process(update,context,sess):
    global db
    text = None
    if(update.message.text is not None):
        text = update.message.text
    #commands command
    if(sess.state == state_create_reply.BEGIN):
        sess.data = ActionCommandObject(text)
        if(db.check_action_command_name_exists(text)):
            update.message.reply_text("Loading '"+text+"' from database.")
            db_data = db.load_action_command(text)
            sess.data.load_from_db(db_data)

            
        sess.state = state_create_reply.NONE
        update.message.reply_text("""COMMANDS:
        /(t)rigger (a)dd
        /(t)rigger (r)emove
        /(r)eply (a)dd
        /(r)eply (r)emove
        /(b)egin
        /(e)xit
        /(p)rint
        /(s)save
        /delete
        """)
    else:
        if(text is not None):
            if(text[0] == "/"):
                split_text = text[1:].lower().split(" ")
                if(len(split_text) == 1):
                    if(split_text[0] in ["exit","e"]):
                        remove_session(sess)
                        update.message.reply_text("Exiting trigger reply command mode")
                    elif(split_text[0] in ["begin","b"]):
                        sess.state = state_create_reply.BEGIN
                        update.message.reply_text("Enter name for command (will load existing if it.. well exists)")
                    elif(split_text[0] in ["save","s"]):
                        save_obj = sess.data.make_db_object()
                        db.save_action_command(save_obj[0],save_obj)
                        update.message.reply_text("Saving and exiting trigger reply command mode and exiting")
                        remove_session(sess)
                        
                    elif(split_text[0] in ["print","p"]):
                        update.message.reply_text("Triggers:")
                        for k in sess.data.actions:
                            #print(k)
                            act = sess.data.actions[k]
                            if(act[1] == message_types.STICKER):
                                update.message.reply_text(act[0])
                            elif(act[1] == message_types.TEXT):
                                update.message.reply_text(act[0])
                        update.message.reply_text("Replies:")
                        for k in sess.data.replies:
                            #print(k)
                            act = sess.data.replies[k]
                            if(act[1] == message_types.STICKER):
                                update.message.reply_sticker(act[0])
                            elif(act[1] == message_types.TEXT):
                                update.message.reply_text(act[0])
                        update.message.reply_text(str(sess.data))
                        print(str(sess.data))
                    elif(split_text[0] in ["delete"]):
                        db.remove_action_command(sess.data.object_id)
                        remove_session(sess)
                        update.message.reply_text("Deleting trigger command and exiting.")
                elif(len(split_text) == 2):
                    if(split_text[0] in ["trigger","t"]):
                        if(split_text[1]in ["add","a"]):
                            sess.state = state_create_reply.ACTIONS_ADD
                            update.message.reply_text("Send text or stickers (uses emoji) you wish to add as a trigger")
                        elif(split_text[1] in ["remove","r"]):
                            sess.state = state_create_reply.ACTIONS_REMOVE
                            update.message.reply_text("Send text or stickers (uses emoji) you wish to remove as a trigger")
                        else:
                            update.message.reply_text("Not a valid trigger command.")
                    elif(split_text[0] in ["reply","r"]):
                        if(split_text[1]in ["add","a"]):
                            sess.state = state_create_reply.REPLY_ADD
                            update.message.reply_text("Send stickers, text or gifs you wish to add as a reply")
                        elif(split_text[1] in ["remove","r"]):
                            sess.state = state_create_reply.REPLY_REMOVE
                            update.message.reply_text("Send stickers, text or gifs you wish to remove as a reply")
                        else:
                            update.message.reply_text("Not a valid reply command.")
                    else:
                        update.message.reply_text("Not a valid command.")
                else:
                    update.message.reply_text("Not a valid command.")
            else:
                if(sess.state == state_create_reply.ACTIONS_ADD):
                    sess.data.add_action(text,message_types.TEXT)
                    update.message.reply_text("Added Trigger:")
                    update.message.reply_text(text)
                elif(sess.state == state_create_reply.ACTIONS_REMOVE):
                    sess.data.remove_action(text,message_types.TEXT)
                    update.message.reply_text("Removed Trigger:")
                    update.message.reply_text(text)
                elif(sess.state == state_create_reply.REPLY_ADD):
                    sess.data.add_reply(text,message_types.TEXT)
                    update.message.reply_text("Added Reply:")
                    update.message.reply_text(text)
                elif(sess.state == state_create_reply.REPLY_REMOVE):
                    sess.data.remove_reply(text,message_types.TEXT)
                    update.message.reply_text("Removed Reply:")
                    update.message.reply_text(text)
        elif(update.message.sticker is not None):
            sticker = update.message.sticker.file_id
            sticker_emoji = update.message.sticker.emoji
            if(sess.state == state_create_reply.ACTIONS_ADD):
                sess.data.add_action(sticker_emoji,message_types.STICKER)
                update.message.reply_text("Added Trigger:")
                update.message.reply_text(sticker_emoji)
            elif(sess.state == state_create_reply.ACTIONS_REMOVE):
                sess.data.remove_action(sticker_emoji,message_types.STICKER)
                update.message.reply_text("Removed Trigger:")
                update.message.reply_text(sticker_emoji)
            elif(sess.state == state_create_reply.REPLY_ADD):
                sess.data.add_reply(sticker,message_types.STICKER)
                update.message.reply_text("Added Reply:")
                update.message.reply_sticker(sticker)
            elif(sess.state == state_create_reply.REPLY_REMOVE):
                ret = sess.data.remove_reply(sticker,message_types.STICKER,context.bot)
                if(ret):
                    update.message.reply_text("Removed Reply:")
                    update.message.reply_sticker(sticker)
                else:
                    update.message.reply_text("Failed to remove")
        elif(update.message.animation is not None):
            animation = update.message.animation.file_id
            if(sess.state == state_create_reply.REPLY_ADD):
                sess.data.add_reply(animation,message_types.GIF)
                update.message.reply_text("Added Reply:")
                update.message.reply_animation(animation)
            elif(sess.state == state_create_reply.REPLY_REMOVE):
                ret = sess.data.remove_reply(animation,message_types.GIF,context.bot)
                if(ret):
                    update.message.reply_text("Removed Reply:")
                    update.message.reply_animation(animation)
                else:
                    update.message.reply_text("Failed to remove")
def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')
    update.message.send()
def groups_command(update,context):
    global groups
    update.message.reply_text(groups)

def all_process(update,context):
    #print(update)
    user_id = update.message.from_user.id
    try:
        sess = check_sessions(user_id)

        if(sess is None):
            if(update.message.text is not None):
                message_process(update,context)
            elif(update.message.sticker is not None):
                sticker_process(update,context)
            elif(update.message.animation is not None):
                # print("ANIMATION")
                # print(update.message.animation)
                animation_processor(update,context)

                
        else:
            if(isinstance(sess.state,state_create_reply)):
                ret = create_reply_process(update,context,sess)
            else:
                return
    except Exception as e:
        logger.error("e",exc_info=True)
def animation_processor(update,context):
    global actions_command_controller
    animation = update.message.animation.file_id
    actions_command_controller.run((animation,message_types.GIF),update,context)
def sticker_process(update, context):
    global actions_command_controller
    #print(update.message.sticker)
    sticker = update.message.sticker.emoji
    actions_command_controller.run((sticker,message_types.STICKER),update,context)
    return
def message_process(update, context):
    global groups
    global wait_time_s
    global new_group
    global actions_command_controller
    #print(context.bot.get_chat(update.message.chat.id))
    """Echo the user message."""
    message = update.message.text
    if(update.message.chat.type == "supergroup"):
        group_id = update.message.chat.id
        if group_id not in groups:
            groups[group_id] = new_group.copy()
        #print(groups[group_id],update.message.from_user.id)
        #if for wait time
        if(groups[group_id][2] and update.message.from_user.id == groups[group_id][3]):
           return  _set_wait_time(update,context,group_id)
        
        #if message too short for t
        if len(message) > 3:
            #if for t.
            if(message[:3] == "t. "):
                return _t(update,context,group_id,message)
        if len(message) > 1:
            if message.lower()[0:3] == "tfw":
                return _tfw(update,context,group_id,message)
        
    actions_command_controller.run((message,message_types.TEXT),update,context)
    return
    
    #print("C: ",context)
    #update.message.reply_text(update.message.text)
def _ai_reply(update,context,group_id):
    update.message.reply_text("Hang yourself, you AI fuck.")
    return
def _tfw(update,context,group_id,message):
    global groups
    group_last_time, group_wait_time,_,_ = groups[group_id]
    if(time.time() - group_last_time < group_wait_time):
        return
    send_message = "Its real "
    send_message += message[4:].lower()
    send_message += " hours"
    groups[group_id][0] = time.time()
    context.bot.send_message(group_id,send_message)
def _t(update,context,group_id,message):
    reply = update.message.reply_to_message
    context.bot.send_message(group_id,message,reply_to_message_id = reply.message_id)
    try:
        context.bot.delete_message(group_id,update.message.message_id)
    except:
        return
    return
def _set_wait_time(update,context,group_id):
    print("_set_wait_time")
    global wait_time_s
    global new_group
    global groups
    message = update.message.text
    num = 0
    tmp = ""
    stop = None
    for char_i in range(len(message)):
        char = message[char_i]
        try:
            l = int(char)
            tmp += char
        except:
            stop = char_i
            break
    try:
        print(tmp)
        print(stop)
        num = int(tmp)
    except:
        update.message.reply_text("Unknown time.")
        return
    if(stop is None):
        groups[group_id][1] = num
    else:
        if(message[stop] == "s"):
            groups[group_id][1] = num
        elif(message[stop] == "m"):
            groups[group_id][1] = num*60
        elif(message[stop] == "h"):
            groups[group_id][1] = num*60*60
        else:
            update.message.reply_text("Unknown time.")
            return
    groups[group_id][2] = False
    groups[group_id][3] = None
    message_ = "Wait time updated to: "+str(groups[group_id][1])+" seconds."
    update.message.reply_text(message_)
def set_wait_time(update,context):
    global wait_time_s
    global new_group
    global groups
    global god_users
    print("set_wait_time")
    print(update.message.from_user)
    if(update.message.chat.type != "supergroup"):
        return
    if(update.message.from_user.id not in god_users):
        #user = context.bot.get_chat_member(update.message.chat.id,update.message.from_user.id)
        message = "Fuck off cunt"
        update.message.reply_text(message)
        return
    group_id = update.message.chat.id
    if group_id not in groups:
        groups[group_id] = new_group.copy()
    groups[group_id][2] = True
    #print(update.message.to_dict().keys())
    groups[group_id][3] = update.message.from_user.id
    update.message.reply_text("Write a time in seconds to set the wait time.")


# def bye(update,context):
#     me = context.bot.get_me()
#     context.bot.kick_chat_member(update.message.chat.id,me.id)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
    #context.bot.send_message(god_users[0],str(context.error))
    #print(traceback.print_last())

# start - Guess it starts 
# reload_actions_controller - Reloads the action brain thing 
# new_action_reply - Opens the action command builder 
# set_wait_time - Sets how often the bot can send non-action messages
# print_actions - Prints action commands that are in the database.
def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1004491664:AAG3edOAxN6qUvsbdazg15wf8CBv4pWzbWQ", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("reload_actions_controller", reload_actions_controller))
    dp.add_handler(CommandHandler("new_action_reply", new_action_reply_command))
    dp.add_handler(CommandHandler("print_actions", print_actions_command))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("groups", groups_command))
    dp.add_handler(CommandHandler("set_wait_time",set_wait_time))
    #dp.add_handler(CommandHandler("bye",bye))
    # on noncommand i.e message - echo the message on Telegram
    #dp.add_handler(MessageHandler(Filters.text, message_process))
    dp.add_handler(MessageHandler(Filters.all, all_process))
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
