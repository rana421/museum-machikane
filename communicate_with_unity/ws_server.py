#https://tech.morikatron.ai/entry/2020/07/20/100000
#上記のサイトを参考にしました。
import asyncio
import websockets
import json
import search_database


address = "0.0.0.0"
port = 8001
# 受信コールバック
async def server(websocket, path):
    try:
        # 受信
        received_packet = await websocket.recv()
        receive_msg = json.loads(received_packet.decode())

        print(f"came from :{path} , message: {receive_msg}")

        #ここから送信処理
        if receive_msg["TYPE"] == "COM_TEST":
            test_response = {"TYPE":"COM_TEST","RESPONSE":"Hello! Unity! from Python"}
            packet = json.dumps(test_response , ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)
        
        elif receive_msg["TYPE"] == "USER_INPUT":

            # 送信
            user_input = receive_msg["user_input"]
            user_input .replace('\u200b', ' ') #半角の文字コードを消している
            user_input .replace('\u3000', ' ') #全角の文字コードを消している
            print(user_input)
            #await asyncio.sleep(1)
            QUERY = SDB.make_QUERY(user_input=user_input)
            print_query = ""
            for query in QUERY:
                print_query += query +","
            QUERY_DICT = {"TYPE": "QUERY" ,"QUERY":print_query }
            packet = json.dumps(QUERY_DICT, ensure_ascii=False).encode('utf-8')
            #packet = json.dumps(QUERY_DICT)
            await websocket.send(packet)

            #await asyncio.sleep(1)
            index_num, prefecture, museum_name, exhibition_name, exhibition_reason = SDB.make_output()
            ANS_DICT = {"TYPE" : "ANSWER", "prefecture":prefecture,"museum_name": museum_name,"exhibition_name":exhibition_name,"exhibition_reason":exhibition_reason}
            packet = json.dumps(ANS_DICT, ensure_ascii=False).encode('utf-8')
            #packet = json.dumps(ANS_DICT)
            await websocket.send(packet)

    except websockets.ConnectionClosedError:
        print("クライアント側により切断されました。")
        
    finally:
        await websocket.close()  # 必ず接続を閉じる




SDB = search_database.Search_database()
start_server = websockets.serve(server, address, port)
# サーバー立ち上げ
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()