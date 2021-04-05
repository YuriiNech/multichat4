import os
import channels.asgi
print("in asgi.py _____22222222222222_____________2222222222222222_______________________")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatproject.settings")
channel_layer = channels.asgi.get_channel_layer()
