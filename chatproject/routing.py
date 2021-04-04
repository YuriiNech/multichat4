# from channels.routing import route
from channels.staticfiles import StaticFilesConsumer
# from chatapp import consumers
channel_routing ={
    'http.request': StaticFilesConsumer(),

    'websocket.connect': 'chatapp.consumers.ws_connect',
    'websocket.receive': 'chatapp.consumers.ws_message',
    'websocket.disconnect': 'chatapp.consumers.ws_disconnect',

}
