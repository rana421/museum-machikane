import socket
import pickle
import select
import time
import json
import random

data = {1: "Apple", 2: "Orange"}
message = "HELLO,Unity!"
IP_ADRESS = "0.0.0.0"
PORT = 4001

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((IP_ADRESS, PORT))  # IPとポート番号を指定します
s.listen(5)
#s.setblocking(0)


while True:
    clientsocket, address = s.accept()
    #print(f"Connection from {address} has been established!")
   

    count =0
    full_msg = b''
    #msg = clientsocket.recv(1024)
    #print(msg.decode('UTF-8'))
    #clientsocket.close() 
    
    while True:
        #print(count)
        
        ready = select.select([clientsocket],[],[],0.005)

        if ready[0] :
            msg = clientsocket.recv(4096)
            full_msg += msg
           
        else:
            break      
        count +=1

    #print(full_msg.decode('UTF-8'))

    msg = full_msg
    json_msg = json.loads(msg.decode('UTF-8'))

    neuron_data ={}
    for data in json_msg.values():
        neuron_data[(data["x"],data["y"])] = data["value"]
    
    sigma =0
    for data in neuron_data.values():
        sigma+= data
    
    print(sigma)

    
    response = random.randint(0,3)
    clientsocket.send(str(response).encode("UTF-8"))
    
    clientsocket.close() #これがないと通信が終わらない
    #print(neuron_data[(15,15)])

