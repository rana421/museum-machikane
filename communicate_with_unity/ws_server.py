#https://tech.morikatron.ai/entry/2020/07/20/100000
#上記のサイトを参考にしました。
import asyncio
import websockets
import json
address = "localhost"
port = 8001
# 受信コールバック
async def server(websocket, path):
    # 受信
    received_packet = await websocket.recv()
    dictionary = json.loads(received_packet.decode())
    print("{}: {}".format(path, dictionary))
    # 送信
    dictionary['message'] = 'Message from Server'
    dictionary['bool'] = False
    packet = json.dumps(dictionary).encode()

    await asyncio.sleep(3) #テストで止めてみる

    await websocket.send(packet)
start_server = websockets.serve(server, address, port)
# サーバー立ち上げ
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()