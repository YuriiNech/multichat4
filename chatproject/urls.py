from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from chatapp.views import chat, register, accounts, logout_view, get_privat_chat, create_privat_chat, privat_chat
from chatapp.views import is_username_exists, change_password, leave_chat, users, show, clear_db, about

urlpatterns = [
    url(r'^about/', about),
    url(r'^$', chat),
    url(r'^admin/', admin.site.urls),
    url(r'^chat/', chat),
    url(r'^privat_chat/', privat_chat),
    url(r'^get_privat_chat/', get_privat_chat),
    url(r'^create_privat_chat/', create_privat_chat),
    url(r'^register/', register),
    url(r'^login/', login),
    url(r'^logout/', logout_view),
    url(r'^accounts/profile/', chat),
    url(r'^is_username_exists/', is_username_exists),
    url(r'^change_password/', change_password),
    url(r'^leave/', leave_chat),
    url(r'^users/', users),
    url(r'^show/', show),
    url(r'^clear_db/', clear_db)
]
