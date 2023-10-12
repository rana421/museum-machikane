#https://uepon.hatenadiary.com/entry/2018/12/28/203627
#ws_severのやつとは別に上記を参考にしました。

import asyncio
import websockets
import json
loop = asyncio.get_event_loop()
# 接続
uri = "ws://localhost:8001"
websocket = loop.run_until_complete(websockets.connect(uri))
# 送信

user_input =  '浮世絵に興味があります！'


dictionary = {'user_input':user_input}
packet = json.dumps(dictionary).encode()
# loop.run_until_complete(websocket.send(packet))
# # 受信
# received_packet = loop.run_until_complete(websocket.recv())
# dictionary = json.loads(received_packet.decode())
# print(dictionary)
# # 終了
# loop.run_until_complete(websocket.close())
# loop.close()
# print("Finish.")

async def loop():
    async with websockets.connect(uri) as websocket:
        await websocket.send(packet)
        print(">> sent a packet")
        while True:

            try:
                receiveData = await websocket.recv()
                dictionary = json.loads(receiveData.decode())
                #print(f"{dictionary}")

                if dictionary["TYPE"] == "QUERY":
                    print(dictionary["QUERY"])
                
                elif dictionary["TYPE"] == "ANSWER":
                    print("________________________________________________________")
                    print( "@"+ dictionary["prefecture"])
                    print("「"+dictionary["museum_name"] + "  "+dictionary["exhibition_name"] +"」")
                    #print(dictionary["exhibition_name"])
                    print("______AIからの一言______")
                    print(dictionary["exhibition_reason"])
                    print("________________________________________________________")
            
            except websockets.exceptions.ConnectionClosedOK:
                print("CLOSED")
                break
asyncio.get_event_loop().run_until_complete(loop())