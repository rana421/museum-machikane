#https://tech.morikatron.ai/entry/2020/07/20/100000
#上記のサイトを参考にしました。
import asyncio
import websockets
import json
import wave
from module import pdf, print_pdf, audio_input, search_database

import os

address = "0.0.0.0"
port = 8001
timeout = 60 * 5

SDB = search_database.Search_database()

# 受信コールバック
async def server(websocket, path):
    async for msg in websocket:
        # JSONとしての解析を試みる
        try:
            receive_msg = json.loads(msg.decode())
            # print(f">> received message: {receive_msg}")
        except Exception:
            # 音声ファイルの場合の処理
            print(">> 音声ファイルを受信しました\n")
            print(">> 音声認識中...\n")
            audio_output = "./audio/tmp.wav"
            with wave.open(audio_output, "wb") as ww:
                ww.setparams(audio_params)
                #convert numpy arrays to binary format
                ww.writeframes(msg)

            user_input = audio_input.recognize_audio("./audio/tmp.wav")
            print(">> 音声入力の終了\n")
            print(">> 入力された内容：", user_input, "\n\n")

            audio_dict = {"TYPE": "AUDIO" ,"USER_INPUT": user_input}
            audio_packet = json.dumps(audio_dict, ensure_ascii=False).encode('utf-8')
            await websocket.send(audio_packet)

        if receive_msg["TYPE"] == "AUDIO_PARAMS":
            # audio ファイルのパラメータを受信
            audio_params = wave._wave_params(*receive_msg["PARAMS"].values())
            search_mode = receive_msg["MODE"]

        elif receive_msg["TYPE"] == "USER_INPUT":
            search_mode = receive_msg["MODE"]

            user_input = receive_msg["user_input"]
            user_input.replace('\u200b', ' ') #半角の文字コードを消している
            user_input.replace('\u3000', ' ') #全角の文字コードを消している
            query = SDB.make_QUERY(user_input=user_input)
            print_query = ",".join(query)

            # Quryを送信
            query_dict = {"TYPE": "QUERY", "QUERY": print_query}
            packet = json.dumps(query_dict, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)

            # 検索結果を送信
            _, prefecture, museum_name, exhibition_name, exhibition_reason, url = SDB.make_output(mode=search_mode)
            answer_dict = {
                "TYPE" : "ANSWER",
                "prefecture": prefecture,
                "museum_name": museum_name,
                "exhibition_name": exhibition_name,
                "exhibition_reason": exhibition_reason
            }
            answer_packet = json.dumps(answer_dict, ensure_ascii=False).encode('utf-8')
            await websocket.send(answer_packet)

        elif receive_msg["TYPE"] == "PRINT":
            print(">> PDFを作成し印刷を開始します\n")
            # PDFを印刷
            pdf.create_PDF(user_input, museum_name, exhibition_name, exhibition_reason, url)
            # print_pdf.send_printer("./sample.pdf", "Brother MFC-L2750DW E302")
            # print_pdf.send_printer("./sample.pdf", "EW-M571T Series(ネットワーク)")

            # CLOSEを送信
            CLOSE_DICT = {"TYPE" : "CLOSE"}
            packet = json.dumps(CLOSE_DICT, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)

            print(">> WEBSOCKET CLOSED\n")


        # テスト用
        elif receive_msg["TYPE"] == "COM_TEST":
            TEST_DICT = {"TYPE": "COM_TEST" ,"RESPONSE":"Hello Unity From Python!" }
            packet = json.dumps(TEST_DICT, ensure_ascii=False).encode('utf-8')
            await websocket.send(packet)
            print("sent a test message to unity")


async def main():
    async with websockets.serve(server, address, port, ping_interval = None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())