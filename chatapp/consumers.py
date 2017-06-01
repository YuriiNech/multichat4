import json
import time
from datetime import datetime
from django.core.mail import send_mail
from django.contrib.auth.models import User, Group
from channels.channel import Group, Channel
from channels.auth import channel_session_user_from_http, channel_session_user
import sqlite3


@channel_session_user_from_http
def ws_connect(message):

    # accept reply_channel
    message.reply_channel.send({'accept': True})

    # connection to DB
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    # get path and add user in Group(path)
    path = message.content['path'].strip('/')
    Group(path).add(message.reply_channel)

    if (path == "chat"):
        # limit messages for show
        rows_limit = 100
        cur.execute("SELECT COUNT() FROM chatapp_chat")
        curSize = cur.fetchone()[0]
        offset = (curSize - rows_limit) if ((curSize - rows_limit) > 0) else 0
        t = (rows_limit, offset)
        cur.execute(
            "SELECT message, username, time FROM chatapp_chat LIMIT ? OFFSET ? ", t)
    else:
        # get id of privat chat
        chat_id = int(path[4:])

        # set user_on = true and new_message = false in chat with correct chat_id
        user_id = message.user.id
        t = (1, 0, chat_id, user_id)
        cur.execute("UPDATE chatapp_privat_chat_user SET user_on = ?, new_message = ? WHERE chat_id = ? and user_id =?", t)
        conn.commit()

        # search for messages in correct chat_id
        t = (chat_id,)
        cur.execute("SELECT message, username, time FROM chatapp_privat_chat  WHERE chat_id = ?", t)

    # send massages from DB
    results = cur.fetchall()
    for res in results:
        try:
            time = datetime.strptime(res[2].rpartition('.')[0], "%Y-%m-%d %H:%M:%S")
            time = datetime.strftime(time, "%d.%m.%y %H:%M:%S")
        except:
            time = res[2]

        message.reply_channel.send({'text': json.dumps({'message': res[0],
                                                'username': res[1],
                                                'time': time})})


    if not message.user.id:
        conn.close()
        return

    # add reply_channel for user in DB
    channel_name = message.reply_channel.name
    user_id = message.user.id
    t = (user_id, channel_name)
    cur.execute("INSERT INTO chatapp_reply_channel (user_id, reply_channel) VALUES (?, ?)", t)
    conn.commit()

    # Check for new messages in other chats
    t = (message.user.id, 1)
    cur.execute("SELECT reply_channel FROM chatapp_privat_chat_user, chatapp_reply_channel WHERE "
                "chatapp_privat_chat_user.user_id = chatapp_reply_channel.user_id and " 
                "chatapp_privat_chat_user.user_id = ? and new_message = ?", t)
    results = cur.fetchall()
    if (results):

        try:
            Channel(results[0][0]).send({'text': json.dumps({'message': "New message in another private chat",
                                                      'username': " - ",
                                                      'time': 0})})
        except:
            print("ERROR results =", results)

    conn.close()


@channel_session_user
def ws_message(message):

    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    path = message.content['path'].strip('/')

    # add message to DB
    if (path == "chat"):
        t = (message.user.username, message.content['text'], datetime.now())
        cur.execute("INSERT INTO chatapp_chat (username, message, time) VALUES (?, ?, ?)", t)
        conn.commit()
    else:
        # get privat chat id
        chat_id = path[4:]
        chat_id = int(chat_id)
        t = (chat_id, message.user.username, message.content['text'], datetime.now())

        # add message to DB with correct chat id
        cur.execute("INSERT INTO chatapp_privat_chat (chat_id, username, message, time) VALUES (?, ?, ?, ?)", t)
        conn.commit()

        # set new_message = true for users with user_on=false
        t = (1, chat_id, 0)
        cur.execute("UPDATE chatapp_privat_chat_user SET new_message = ? WHERE chat_id = ? and  user_on = ?", t)
        conn.commit()

        # send "new message" for users with new_messages = true
        t = (chat_id, 1,)
        cur.execute(
            "SELECT reply_channel FROM chatapp_privat_chat_user, chatapp_reply_channel WHERE chatapp_privat_chat_user.user_id = chatapp_reply_channel.user_id and chat_id = ? and new_message = ?",
            t)
        results = cur.fetchall()
        for res in results:
            try:
                Channel(res[0]).send({'text': json.dumps({'message': "New message in another private chat",
                                                      'username': " - ",
                                                      'time': 0})})
            except:
                print("ERROR Channel name must be a valid unicode string" )


    Group(path).send({'text': json.dumps({'message': message.content['text'],
                                            'username': message.user.username,
                                            'time': datetime.strftime(datetime.now(), "%d.%m.%y %H:%M:%S")})})

    conn.close()


@channel_session_user
def ws_disconnect(message):
    path = message.content['path'].strip('/')

    if not message.user.id:
        Group(path).discard(message.reply_channel)
        return

    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    # delete reply_channel of user from DB
    user_id = int(message.user.id)
    t = (user_id, )
    cur.execute("DELETE FROM chatapp_reply_channel WHERE user_id = ? ", t)
    conn.commit()

    if (path != "chat"):

        # get privat chat id
        chat_id = path[4:]
        chat_id = int(chat_id)

        # set user_on = false in correct chat id
        t = (0, chat_id, user_id)
        cur.execute("UPDATE chatapp_privat_chat_user SET user_on = ? WHERE chat_id = ? and user_id = ?", t)
        conn.commit()

    Group(path).discard(message.reply_channel)
    conn.close()
