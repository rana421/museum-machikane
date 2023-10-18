#https://tech.morikatron.ai/entry/2020/07/20/100000
#上記のサイトを参考にしました。
import asyncio
import websockets
import json
import search_database
from module import pdf, print_pdf

address = "0.0.0.0"
port = 8001
timeout = 60 * 5

# 受信コールバック
async def server(websocket, path):
    try:
        # 受信
        #received_packet = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        received_packet = await websocket.recv()
        receive_msg = json.loads(received_packet.decode())

        print(f">> received message: {receive_msg}")
        #>> received message: {'TYPE': 'USER_INPUT', 'user_input': 'スラムダンクが好きです', '_is_kansai_only': 'False'}という形で帰ってきます

        #ここから送信処理
        if receive_msg["TYPE"] == "USER_INPUT":
            # 送信
            user_input = receive_msg["user_input"]
            user_input.replace('\u200b', ' ') #半角の文字コードを消している
            user_input.replace('\u3000', ' ') #全角の文字コードを消している
            QUERY = SDB.make_QUERY(user_input=user_input)
            # print_query = ""
            # for query in QUERY:
            #     print_query += query +","
            # Quryを送信
            QUERY_DICT = {"TYPE": "QUERY" ,"QUERY":QUERY }
            packet = json.dumps(QUERY_DICT, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)

            # 検索結果を送信
            index_num, prefecture, museum_name, exhibition_name, exhibition_reason, url = SDB.make_output()
            ANS_DICT = {"TYPE" : "ANSWER", "prefecture": prefecture, "museum_name": museum_name, "exhibition_name": exhibition_name, "exhibition_reason": exhibition_reason}
            packet = json.dumps(ANS_DICT, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)

            # PDFを印刷
            pdf.create_PDF(museum_name, exhibition_name, exhibition_reason, url)
            # print_pdf.send_printer("./sample.pdf", "Brother MFC-L2750DW E302")
            # print_pdf.send_printer("./sample.pdf", "EW-M571T Series(ネットワーク)")
            PRINT_DICT = {"TYPE" : "PRINT"}
            packet = json.dumps(PRINT_DICT, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)

        elif receive_msg["TYPE"] == "COM_TEST":
            TEST_DICT = {"TYPE": "COM_TEST" ,"RESPONSE":"Hello Unity From Python!" }
            packet = json.dumps(TEST_DICT, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)
            print("sent a test message to unity")
            # CLOSEを送信
            # await asyncio.sleep(5)
            # CLOSE_DICT = {"TYPE" : "CLOSE"}
            # packet = json.dumps(CLOSE_DICT, ensure_ascii=False).encode('utf-8')
            # await websocket.send(packet)


    except websockets.ConnectionClosedError:
        print("クライアント側により切断されました。")

    finally:
        await websocket.close()  # 必ず接続を閉じる

# async def main():
#     async with websockets.serve(server, address, port, ping_interval = None):
#         await asyncio.Future()

# if __name__ == "__main__":
#     SDB = search_database.Search_database()
#     asyncio.run(main())

#上記のコードだとunityとの連携でうまく動かなかったので一応以下のやつで動作させます
SDB = search_database.Search_database()
start_server = websockets.serve(server, address, port)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()