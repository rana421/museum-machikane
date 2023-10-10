from websocket_server import WebsocketServer
from datetime import datetime

def new_client(client, server):
    server.send_message_to_all(datetime.now().isoformat() + ": new client joined!")
    
    IP_address = client['address'][0]
    Port = client['address'][1]
    print(f'New Client Connected From {IP_address},{Port}')
    print(client)



def message_received(client, server, message):
        print("client({}) said: {}".format(client['id'], message))
        server.send_message(client,"HELLO!")
        



server = WebsocketServer(host='0.0.0.0',port = 9999)
server.set_fn_new_client(new_client)
server.set_fn_message_received(message_received) 
server.run_forever()