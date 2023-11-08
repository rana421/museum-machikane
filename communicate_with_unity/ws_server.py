import asyncio
import websockets
import json
from distutils.util import strtobool
import sys
sys.path.append("./../")

import os
os.chdir(os.path.dirname(os.path.abspath(__file__))) #カレントディレクトリを固定

from PDFcreator.pdf_create import create_PDF
from database.search_database2 import Search_database
#from database.search_database import Search_database
from printer.print_pdf import send_printer
from speech2text.audio_input import recognize_audio

address = "0.0.0.0"
port = 8001
timeout = 60 * 5
do_print = True

audio_output = "./audio/tmp.wav"
user_input  = ""
is_kansai_only = True
SDB = Search_database()

# 受信コールバック
async def server(websocket, path):
    global user_input,is_kansai_only
    async for msg in websocket:
        # JSONとしての解析を試みる
        try:
            receive_msg = json.loads(msg.decode('utf-8'))
        except Exception:
            # 音声ファイルの場合の処理
            print(">> 音声ファイルを受信しました\n")
            print(">> 音声認識中...\n")
            received_chunks = []
            while msg:
                received_chunks.append(msg)
                msg = await websocket.recv()

            with open(audio_output, "wb") as f:
                for data in received_chunks:
                    f.write(data)

            user_input = recognize_audio("./audio/tmp.wav")
            print(">> 音声入力の終了\n")
            print(">> 入力された内容：", user_input, "\n\n")

            audio_dict = {"TYPE": "AUDIO" ,"user_input": user_input}
            audio_packet = json.dumps(audio_dict, ensure_ascii=False).encode('utf-8')
            await websocket.send(audio_packet)
            continue

        try:
            if receive_msg["TYPE"] == "USER_INPUT":
                is_kansai_only = bool(strtobool(str(receive_msg["_is_kansai_only"]))) #stringからboolへ変換

                user_input = receive_msg["user_input"]
                user_input.replace('\u200b', ' ') #半角の文字コードを消している
                user_input.replace('\u3000', ' ') #全角の文字コードを消している
                print(f"user_input: {user_input}  _is_kansi_only: {is_kansai_only}")
                query = SDB.make_QUERY(user_input=user_input)

                # Quryを送信
                query_dict = {"TYPE": "QUERY", "QUERY": query}
                packet = json.dumps(query_dict, ensure_ascii=False).encode('utf-8')
                await websocket.send(packet)

                # 検索結果を送信
                results = SDB.make_output(is_kansai_only=is_kansai_only)
                _, prefecture, museum_name, exhibition_name, exhibition_reason, url = results
                answer_dict = {
                    "TYPE" : "ANSWER",
                    "prefecture": prefecture,
                    "museum_name": museum_name,
                    "exhibition_name": exhibition_name,
                    "exhibition_reason": exhibition_reason
                }
                answer_packet = json.dumps(answer_dict, ensure_ascii=False).encode('utf-8')
                await websocket.send(answer_packet)


            elif receive_msg["TYPE"] == "PRINT_START":
                print(">> PDFを作成し印刷を開始します\n")
                # PDFを印刷
                create_PDF(user_input, museum_name, exhibition_name, exhibition_reason, url, is_kansai_only)

                if(do_print):
                    send_printer("./sample.pdf","EPSON_EW_M630T_Series")

                print(">> PDF印刷処理中...")
                await asyncio.sleep(15) #ここは事前準備によって変えよう！

                # PRINT FINISHを送信
                FINISH_DICT = {"TYPE" : "PRINT_FINISH"}
                packet = json.dumps(FINISH_DICT, ensure_ascii=False).encode('utf-8')
                await websocket.send(packet)

                print(">> WEBSOCKET CLOSED\n")
                #await websocket.close()


            # テスト用
            elif receive_msg["TYPE"] == "COM_TEST":
                TEST_DICT = {"TYPE": "COM_TEST" ,"RESPONSE":"Hello Unity From Python!" }
                packet = json.dumps(TEST_DICT, ensure_ascii=False).encode('utf-8')
                await websocket.send(packet)
                print("sent a test message to unity")

        except websockets.exceptions.ConnectionClosedError:
            print(">> WEBSOCKET CLOSED\n")
            await websocket.close()
            continue


async def main():
    async with websockets.serve(server, address, port, ping_interval = None):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
