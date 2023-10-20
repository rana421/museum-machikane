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

SDB = search_database.Search_database()

# 受信コールバック
async def server(websocket, path):
    while True:
        try:
            # 受信
            received_packet = await asyncio.wait_for(websocket.recv(), timeout=timeout)
            receive_msg = json.loads(received_packet.decode())

            print(f">> received message: {receive_msg}")

            #ここから送信処理
            if receive_msg["TYPE"] == "USER_INPUT":
                # 送信
                user_input = receive_msg["user_input"]
                user_input.replace('\u200b', ' ') #半角の文字コードを消している
                user_input.replace('\u3000', ' ') #全角の文字コードを消している
                QUERY = SDB.make_QUERY(user_input=user_input)
                print_query = ""
                for query in QUERY:
                    print_query += query +","
                # Quryを送信
                QUERY_DICT = {"TYPE": "QUERY" ,"QUERY":print_query }
                packet = json.dumps(QUERY_DICT, ensure_ascii=False).encode('utf-8')
                await websocket.send(packet)

                # 検索結果を送信
                index_num, prefecture, museum_name, exhibition_name, exhibition_reason, url = SDB.make_output()
                ANS_DICT = {"TYPE" : "ANSWER", "prefecture": prefecture, "museum_name": museum_name, "exhibition_name": exhibition_name, "exhibition_reason": exhibition_reason}
                packet = json.dumps(ANS_DICT, ensure_ascii=False).encode('utf-8')
                await websocket.send(packet)

            elif receive_msg["TYPE"] == "PRINT":
                print(">> PDFを作成し印刷を開始します")
                # PDFを印刷
                pdf.create_PDF(museum_name, exhibition_name, exhibition_reason, url)
                # print_pdf.send_printer("./sample.pdf", "Brother MFC-L2750DW E302")
                # print_pdf.send_printer("./sample.pdf", "EW-M571T Series(ネットワーク)")

                # CLOSEを送信
                CLOSE_DICT = {"TYPE" : "CLOSE"}
                packet = json.dumps(CLOSE_DICT, ensure_ascii=False).encode('utf-8')
                await websocket.send(packet)

        except websockets.ConnectionClosedError:
            print("クライアント側により切断されました。")

        finally:
            await websocket.close()  # 必ず接続を閉じる
            break

async def main():
    async with websockets.serve(server, address, port, ping_interval = None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
