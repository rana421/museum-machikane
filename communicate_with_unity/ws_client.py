#https://uepon.hatenadiary.com/entry/2018/12/28/203627
#ws_severのやつとは別に上記を参考にしました。
#使用方法：ws_Server.pyを先に起動しておいてから、コマンドプロンプトかなんかでこのディレクトリ上で「python ws_client.py」を実行してください
import asyncio
import websockets
import json
loop = asyncio.get_event_loop()
# 接続
uri = "ws://localhost:8001"
websocket = loop.run_until_complete(websockets.connect(uri))
# 送信

print("\n\n>>希望の展示についてお聞かせください！\n")
user_input = input("Input: ") 
#user_input =  '浮世絵に興味があります！'


dictionary = {"TYPE":"USER_INPUT",'user_input':user_input}
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
        print("\n\n>>検索ワードを作成中...")

        while True:

            try:
                receiveData = await websocket.recv()
                dictionary = json.loads(receiveData.decode())
                #print(f"{dictionary}")

                if dictionary["TYPE"] == "QUERY":
                    print("_____________________________________________________________________________________")
                    print("\n>>提案された検索ワード：")
                    print(dictionary["QUERY"])
                    print("_____________________________________________________________________________________")
                    print("\n>>展示を検索中...")
                
                elif dictionary["TYPE"] == "ANSWER":
                    print("\n_____________________________________________________________________________________")
                    print("[検索結果]\n")
                    print( "@"+ dictionary["prefecture"])
                    print("「"+dictionary["museum_name"] + "  "+dictionary["exhibition_name"] +"」")
                    #print(dictionary["exhibition_name"])
                    print("\n______ミュージアム同好会botからの一言______")
                    print(dictionary["exhibition_reason"])
                    print("_____________________________________________________________________________________")
            
            except websockets.exceptions.ConnectionClosedOK:
                print("CLOSED")
                break
asyncio.get_event_loop().run_until_complete(loop())