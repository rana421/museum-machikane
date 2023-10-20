# https://uepon.hatenadiary.com/entry/2018/12/28/203627
# ws_severのやつとは別に上記を参考にしました。
# 使用方法：ws_Server.pyを先に起動しておいてから、コマンドプロンプトかなんかでこのディレクトリ上で「python ws_client.py」を実行してください
import asyncio
import websockets
import json
# TODO: ChatGPTの出力の時間を計測する

uri = "ws://localhost:8001"
timeout = 60 * 5


async def amain():
    async with websockets.connect(uri, close_timeout=timeout, ping_timeout=None) as websocket:
        print(">> 同好会botにようこそ！\n")
        print(">> 同好会botは、あなたの希望に合った展示を提案します！\n")
        print(">> 希望の展示についてお聞かせください！\n")

        print(">> 音声入力の開始")

        audio_file = "./audio/test.wav"
        print(">> 音声の認識中...")
        with open(audio_file, "rb") as f:
            data = f.read()

        # dictionary = {"TYPE": "AUDIO", "DATA": data}
        # packet = json.dumps(dictionary).encode()
        await websocket.send(data)


        async for msg in websocket:
            receive_msg = json.loads(msg.decode())
            # print(f">> received message: {receive_msg}")

            if receive_msg["TYPE"] == "AUDIO":
                # user_input = input("Input: ")
                # user_input = '浮世絵に興味があります！'
                user_input = receive_msg["USER_INPUT"]

                print(">> 音声入力の終了")
                print(">> 入力された内容：", user_input)

                dictionary = {"TYPE": "USER_INPUT", "user_input": user_input}
                packet = json.dumps(dictionary).encode()
                await websocket.send(packet)
                print("\n\n>> 検索しています...")

            elif receive_msg["TYPE"] == "QUERY":
                print("\n>> 提案された検索ワード：")
                print(receive_msg["QUERY"])
                print("\n>> 展示を検索中...")

            elif receive_msg["TYPE"] == "ANSWER":
                print("[検索結果]\n")
                print( "@"+ receive_msg["prefecture"])
                print("「"+receive_msg["museum_name"] + "  "+receive_msg["exhibition_name"] +"」")
                #print(receive_msg["exhibition_name"])
                print("\n--------同好会botからの一言--------")
                print(receive_msg["exhibition_reason"], end="\n\n")

                # print命令を送信
                print(">> 結果をPDFで印刷します\n")
                dictionary = {"TYPE": "PRINT"}
                packet = json.dumps(dictionary).encode()
                await websocket.send(packet)

            elif receive_msg["TYPE"] == "CLOSE":
                print(">> WEBSOCKET CLOSED")
                await websocket.close()
                break


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        # asyncio.run(amain())
        loop.run_until_complete(amain())
    except KeyboardInterrupt:
        pass