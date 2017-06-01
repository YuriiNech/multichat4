from django.shortcuts import render, redirect, render_to_response
from django.template.context_processors import csrf
from django.contrib.auth.models import User, Group
from django.contrib.auth import login, logout, authenticate
import sqlite3
import time
from django.http import JsonResponse
from chatapp.models import Privat_Chat_User, Privat_Chat_Name, Chat, Privat_Chat, Reply_Channel
from datetime import datetime, timedelta

def accounts(request):

    return redirect("/chat")


def change_password(request):
    if not request.user.is_authenticated():
        return redirect('/login')
    if request.method == "POST":
        try:
            new_password = request.POST['password1']
            username = request.user.username
            request.user.set_password(new_password)
            request.user.save()
            user = authenticate(username=username, password=new_password)
            if user is not None:
                # the password verified for the user
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect("/chat", {"log": request.user.is_authenticated(), "username": request.user.username, "chat":True})
                else:
                    print("The password is valid, but the account has been disabled!")
            return redirect("/chat")
        except:
            password = request.POST['password']
            data ={"password_correct": request.user.check_password(password)}
            return JsonResponse(data)

    return render(request, 'change_password.html',{"log": request.user.is_authenticated(),
                                                   "username":request.user.username, "chat":1})

def chat(request):

    return render(request, 'chat.html', {"log": request.user.is_authenticated(),
                                         "username":request.user.username,"chat":0})

def create_privat_chat(request):
    if not request.user.is_authenticated():
        return redirect('/login')
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()

    # check for existing chats with the name and userset
    chat_name = request.POST['chat_name']
    users_id = request.POST.getlist("users", default=None)
    userset1 = set()
    for user in users_id:
        userset1.add(int(user))
    userset1.add(request.user.id)
    exist_chat_ids = Privat_Chat_Name.objects.filter(chat_name=chat_name).values_list('id', flat=True)
    if exist_chat_ids:
        for exist_chat_id in exist_chat_ids:
            userset2 = Privat_Chat_User.objects.filter(chat_id=exist_chat_id).values_list('user_id', flat=True)
            userset2 = set(userset2)

            if (userset1 == userset2):
                conn.close()
                return exist_chat_id

    # create new chat
    t = (chat_name,)
    cur.execute("INSERT INTO chatapp_privat_chat_name (chat_name) VALUES (?)", t)
    conn.commit()
    cur.execute("SELECT  id FROM  chatapp_privat_chat_name WHERE rowid = last_insert_rowid()")
    chat_id = cur.fetchone()[0]
    for user_id in userset1:
        t=(chat_id, user_id, 0, 1)
        cur.execute("INSERT INTO chatapp_privat_chat_user (chat_id, user_id, user_on, new_message) VALUES (?, ?, ?, ?)", t)
        conn.commit()
    conn.close()
    return chat_id


def get_privat_chat(request):
    if not request.user.is_authenticated():
        return redirect('/login')

    # get all users
    userset = User.objects.exclude(id = request.user.id).values("id", "username")

    # get all  privat chats of request.user
    conn = sqlite3.connect('db.sqlite3')
    cur = conn.cursor()
    user_id = request.user.id
    t = (int(user_id),)
    cur.execute("SELECT chat_id, chat_name, new_message FROM  chatapp_privat_chat_user, chatapp_privat_chat_name "
                "WHERE chatapp_privat_chat_user.chat_id = chatapp_privat_chat_name.id AND "
                "chatapp_privat_chat_user.user_id = ?", t)
    chatset = cur.fetchall()
    data = {"log": request.user.is_authenticated(), "username":request.user.username,
            "userset":userset, "chatset":chatset, "chat":1}

    return render(request, 'get_privat_chat.html', data)


def is_username_exists(request):

    username_exists = False
    if User.objects.filter(username = request.POST['username']).count():
        username_exists = True

    response = JsonResponse({"username_exists": username_exists})
    return response


def leave_chat(request):
    if not request.user.is_authenticated():
        return redirect('/login')

    if request.method == "POST":
        try:

            chat_id = request.POST["chat_id"]
            user_id = request.user.id
            conn = sqlite3.connect('db.sqlite3')
            cur = conn.cursor()
            t = (int(chat_id),int(user_id),)
            cur.execute("DELETE FROM chatapp_privat_chat_user WHERE chat_id = ? AND user_id = ?", t)
            conn.commit()
            t = (int(chat_id), )
            cur.execute("SELECT user_id FROM chatapp_privat_chat_user WHERE chat_id = ? ", t)
            id = cur.fetchone()
            if not id :
                cur.execute("DELETE FROM chatapp_privat_chat WHERE chat_id = ?", t)
                conn.commit()
                cur.execute("DELETE FROM chatapp_privat_chat_name WHERE id = ?", t)
                conn.commit()
            conn.close()

        except:

            print ("ERROR")

    return redirect( '/chat',
                  {"log": request.user.is_authenticated(), "username": request.user.username})



def logout_view(request):
    logout(request)
    return redirect('/login')


def privat_chat(request):
    if not request.user.is_authenticated():
        return redirect('/login')
    user_id = request.user.id

    if request.method == "POST":
        try:
            # if request for go to existing chat
            chat_id = request.POST["chat_id"]
            chat_name = request.POST["chat_name"]
            print (chat_id)
            print (chat_name)
        except:
            # if request for create a new chat
            users = request.POST.getlist("users", default=None)
            chat_name = request.POST["chat_name"]
            chat_id = create_privat_chat(request)
        data = {"chat_name": chat_name, "chat_id": chat_id, "log": request.user.is_authenticated(),
                       "username": request.user.username, "chat":1}
        return render(request, 'privat_chat.html', data)
    # # Is access allowed?
    # conn = sqlite3.connect('db.sqlite3')
    # cur = conn.cursor()
    # t = (int(chat_id),int(user_id),)
    # cur.execute("SELECT chat_id FROM chatapp_privat_chat_user WHERE chat_id = ? AND user_id = ?", t)
    # id = cur.fetchone()
    # if (id):
    return redirect( '/get_privat_chat')


def register(request):

    if request.method == "POST":
        newusername = request.POST['username']
        password = request.POST['password1']
        email = ''

        try:
            user = User.objects.create_user(newusername, email, password)
            user = authenticate(username=newusername, password=password)
            if user is not None:
                # the password verified for the user
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect("/chat")
                else:
                    print("The password is valid, but the account has been disabled!")
            else:
                # the authentication system was unable to verify the username and password
                print("The username and password were incorrect.")
            return redirect ('/login')
        except:
            data = {"log": request.user.is_authenticated(), "username": request.user.username,
                     "chat": 1}
            return render(request, 'register.html', data)
    data = {"log": request.user.is_authenticated(), "username": request.user.username,"chat": 1}
    return render(request, 'register.html', data)


def show(request):
    if not request.user.is_authenticated():
        return redirect('/login')

    chat_id = request.POST["chat_id"]

    # get all users of private chat

    userset = Privat_Chat_User.objects.filter(chat_id = chat_id).values('user', 'user_on')
    userset1 = []
    for ob in userset:
        username = User.objects.filter(id = ob["user"]).values("username")[0]
        user_on = 0
        if ob["user_on"]:
            user_on = 2
        else:
            if Reply_Channel.objects.filter(user_id = ob["user"]).count():
                user_on = 1

        userset1.append({"user_on":user_on, "username":username["username"] })

    response = JsonResponse(userset1, safe=False)
    return response


def users(request):
    if not request.user.is_authenticated():
        return redirect('/login')
    try:
        user_id = request.POST["user_id"]
        chat_id = request.POST["chat_id"]
        u = Privat_Chat_User(chat_id = chat_id, user_id = user_id, user_on = 0, new_message = 1)
        u.save()
        user = Privat_Chat_User.objects.filter(user_id = user_id).values_list('user_id', flat=True)
        response = JsonResponse({"yes":1})
    except:
        chat_id = request.POST["chat_id"]
        # get all users
        userset = []
        username_exists = False
        userset1 = User.objects.all().values('id', 'username')
        userset2 = Privat_Chat_User.objects.filter(chat_id=chat_id).values_list('user_id', flat=True)
        for user in userset1:

            if user['id'] not in userset2:
                userset.append((user['id'], user['username']))

        response = JsonResponse(userset, safe=False)
    return response


def clear_db(request):
    if not request.user.is_authenticated():
        return redirect('/login')
    user_id = request.user.id
    is_superuser = User.objects.filter(id = user_id).values('is_superuser')[0]
    is_superuser = is_superuser["is_superuser"]
    if not is_superuser:
        return redirect('/chat')

    if request.method == "POST":
        lim = 365
        exp = datetime.now() - timedelta(days=lim, minutes=0)

        g = Chat.objects.filter(time__lt=exp).delete()
        g = Privat_Chat.objects.filter(time__lt=exp).delete()
        users = Privat_Chat_Name.objects.all().values('id')
        for user in users:
            id = user["id"]
            users = Privat_Chat_User.objects.filter(chat_id=id).count()
            if not users:
                chat_name = Privat_Chat_Name.objects.filter(id=id).delete()
    chat_count = Chat.objects.all().count()
    privat_chat_count = Privat_Chat.objects.all().count()
    privat_chat_name_count = Privat_Chat_Name.objects.all().count()
    user_count = User.objects.all().count()
    from os.path import getsize
    file_size = getsize('db.sqlite3')
    file_size = round(file_size / 1048576 , 3)
    data = {"chat_count":chat_count, "privat_chat_count":privat_chat_count, "file_size":file_size,
            "user_count":user_count, "privat_chat_name_count":privat_chat_name_count, "chat":1,
            "log": request.user.is_authenticated(), "username": request.user.username}
    return render (request, "clear_db.html", data)
