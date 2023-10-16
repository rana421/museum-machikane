# https://uepon.hatenadiary.com/entry/2018/12/28/203627
# ws_severのやつとは別に上記を参考にしました。
# 使用方法：ws_Server.pyを先に起動しておいてから、コマンドプロンプトかなんかでこのディレクトリ上で「python ws_client.py」を実行してください
import asyncio
import websockets
import json
from module import audio_input

uri = "ws://localhost:8001"
timeout = 60 * 5

print(">> 同好会botにようこそ！\n")
print(">> 同好会botは、あなたの希望に合った展示を提案します！\n")
print(">> 希望の展示についてお聞かせください！\n")

print(">> 音声入力の開始")
# audio_file =  get_audio()
audio_file = "./audio/test.wav"

# user_input = audio_input.recognize_audio(audio_file)
# user_input = input("Input: ")
user_input = '浮世絵に興味があります！'

print(">> 音声入力の終了")
print(">> 入力された内容：", user_input)

async def amain():
    async with websockets.connect(uri, close_timeout=timeout, ping_timeout=None) as websocket:
        dictionary = {"TYPE": "USER_INPUT", "user_input": user_input}
        packet = json.dumps(dictionary).encode()
        await websocket.send(packet)
        print("\n\n>> 検索しています...")

        while True:
            try:
                receiveData = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                dictionary = json.loads(receiveData.decode())
                #print(f"{dictionary}")

                if dictionary["TYPE"] == "QUERY":
                    print("\n>> 提案された検索ワード：")
                    print(dictionary["QUERY"])
                    print("\n>> 展示を検索中...")

                elif dictionary["TYPE"] == "ANSWER":
                    print("[検索結果]\n")
                    print( "@"+ dictionary["prefecture"])
                    print("「"+dictionary["museum_name"] + "  "+dictionary["exhibition_name"] +"」")
                    #print(dictionary["exhibition_name"])
                    print("\n--------同好会botからの一言--------")
                    print(dictionary["exhibition_reason"])

                elif dictionary["TYPE"] == "PRINT":
                    print(">> 結果をPDFで印刷しています")

                elif dictionary["TYPE"] == "CLOSE":
                    print(">> CLOSE")
                    websocket.close()

            # except asyncio.TimeoutError:
            #     print(">> タイムアウトしました。")
            #     break

            except websockets.exceptions.ConnectionClosedOK:
                print("CLOSED")
                break

            # except Exception as e:
            #     print(e)
            #     break

if __name__ == "__main__":
    # loop = asyncio.new_event_loop()
    # asyncio.set_event_loop(loop)
    try:
        asyncio.run(amain())
        # loop.run_until_complete(amain())
    except KeyboardInterrupt:
        pass