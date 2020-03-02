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

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import telegram
import time
# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

groups = {}
wait_time_s = float(10*60)
new_group = [0,wait_time_s,False,0]
god_users = [904522230]
# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    print(update)
    update.message.reply_text('Hi!')
    print(context.bot.get_me())


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')
    update.message.send()
def groups_command(update,context):
    global groups
    update.message.reply_text(groups)
def message_process(update, context):
    global groups
    global wait_time_s
    global new_group
    
    #print(context.bot.get_chat(update.message.chat.id))
    """Echo the user message."""
    if(update.message.chat.type == "supergroup"):
        group_id = update.message.chat.id
        if group_id not in groups:
            groups[group_id] = new_group.copy()
        #print(groups[group_id],update.message.from_user.id)
        #if for wait time
        if(groups[group_id][2] and update.message.from_user.id == groups[group_id][3]):
           return  _set_wait_time(update,context,group_id)
        message = update.message.text
        #if message too short for t
        if len(message) <= 3:
            return
        #if for t.
        if(message[:3] == "t. "):
            return _t(update,context,group_id,message)
        if len(message) <= 4:
            return
        if message.lower()[0:3] == "tfw":
            return _tfw(update,context,group_id,message)
        
        
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
    send_message += message.lower()
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

def all_process(update,context):
    if(update.message.from_user.id in god_users):
        print("UPDATE")
        print(update)
        print("CONTEXT")
        print(context)
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
