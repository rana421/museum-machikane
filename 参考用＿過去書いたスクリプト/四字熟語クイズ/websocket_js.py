import asyncio
import json
from time import time
import websockets
import nest_asyncio
nest_asyncio.apply() #これをするだけでasyncioが使えるようになる！！！すごい！！！
import threading
import Flask_test2

i =0
message = "preset"
data_dict ={}
change_flags = {}

class data:
  id =0
  name = ""
  message = ""


async def recv(websocket,my_number):
  global data_dict,change_flags
  while True:
    try:
      data = await websocket.recv()
      #message = data.decode()
      data_dict[my_number] = message
      print(data)
      a = change_flags.copy()
      for flag in a:
        change_flags[flag] = "1"
      a.clear()
       
        

        
     
    
    except websockets.exceptions.ConnectionClosedOK:
      print("Closed")
      data_dict.pop(my_number) #popするとデータが消える
      a = change_flags.copy()
      for flag in a:
        change_flags[flag] = "1"
      a.clear()
      break



async def send(websocket,my_number):
  global data_dict,change_flags
  #await websocket.send(str(my_number).encode())
  while True:
    try:
      if change_flags[my_number] =="1":
        #print("ON")
        send_data = json.dumps(data_dict)
        await websocket.send(send_data)
        change_flags[my_number] = "0"

      await asyncio.sleep(0.0001) #めっちゃ早くに（実際は15msくらいらしい？）
    
    except websockets.exceptions.ConnectionClosedOK:
      break

        
    


    


# クライアント接続すると呼び出す
async def accept(websocket, path):
  global i,data_dict,change_flags
  my_number =i
  data_dict[my_number] =""
  change_flags[my_number] = "0"
  i +=1
  loop = asyncio.get_event_loop()
  gather = asyncio.gather(recv(websocket,my_number),send(websocket,my_number))
  loop.run_until_complete(gather)


if __name__ == '__main__':
  start_server = websockets.serve(accept, "0.0.0.0", 9999)
  print('main_Start')
  sub =threading.Thread(target=Flask_test2.Start)
  sub.start()
  print("flask_start")
 
  # 非同期でサーバを待機する。
  asyncio.get_event_loop().run_until_complete(start_server)
  #get_event_loopはノンブロッキングなスレッドらしい
  asyncio.get_event_loop().run_forever()
  
  

  

  


def Start():
  start_server = websockets.serve(accept, "0.0.0.0", 111)
  print('sub_Start')
  
  # 非同期でサーバを待機する。
  asyncio.get_event_loop().run_until_complete(start_server)
  #get_event_loopはノンブロッキングなスレッドらしい
  asyncio.get_event_loop().run_forever()
  
