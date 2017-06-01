from django.db import models
from datetime import datetime
from django.utils.six import python_2_unicode_compatible
from django.contrib.auth.models import User


@python_2_unicode_compatible
class Chat(models.Model):

    time = models.DateTimeField()
    username = models.CharField(max_length=50)
    message = models.CharField(max_length=250)

    def __str__(self):
        return self.message


@python_2_unicode_compatible
class Privat_Chat_Name(models.Model):
    chat_name = models.CharField(max_length=200)

    def __str__(self):
        return self.message


@python_2_unicode_compatible
class Privat_Chat(models.Model):

    chat = models.ForeignKey(Privat_Chat_Name, on_delete=models.CASCADE)
    time = models.DateTimeField()
    username = models.CharField(max_length=50)
    message = models.CharField(max_length=250)

    def __str__(self):
        return self.message


@python_2_unicode_compatible
class Privat_Chat_User(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat = models.ForeignKey(Privat_Chat_Name, on_delete=models.CASCADE)
    user_on = models.IntegerField(default = 0)
    new_message = models.IntegerField(default = 1)

    def __str__(self):
        return self.message


@python_2_unicode_compatible
class Reply_Channel(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reply_channel = models.CharField(max_length=50)

    def __str__(self):
        return self.message
