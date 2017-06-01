from channels.routing import route

channel_routing ={
    'websocket.connect': 'chatapp.consumers.ws_connect',
    'websocket.receive': 'chatapp.consumers.ws_message',
    'websocket.disconnect': 'chatapp.consumers.ws_disconnect',

}
