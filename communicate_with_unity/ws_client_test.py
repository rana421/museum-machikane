# https://uepon.hatenadiary.com/entry/2018/12/28/203627
# ws_severのやつとは別に上記を参考にしました。
# 使用方法：ws_Server.pyを先に起動しておいてから、コマンドプロンプトかなんかでこのディレクトリ上で「python ws_client.py」を実行してください
import asyncio
import websockets
import json
import wave
# TODO: ChatGPTの出力の時間を計測する

uri = "ws://localhost:8001"
timeout = 60 * 5

audio_file = "./audio/test.wav"

# input_type = "audio"
# mode = "kansai"

async def amain():
    async with websockets.connect(uri, close_timeout=timeout, ping_timeout=None) as websocket:
        print(">> 同好会botにようこそ！\n")
        print(">> 同好会botは、あなたの希望に合った展示を提案します！\n")
        print(">> 希望の展示についてお聞かせください！\n")

        print(">> 検索範囲を選択してください")
        print(">> all: 全国の展示を検索")
        print(">> kansai: 関西の展示を検索")
        mode = input("Input: ")

        if mode == "all":
            print(">> 全国の展示を検索します\n")
        else:
            print(">> 関西の展示を検索します\n")

        print(">> 音声入力かキーボード入力かを選択してください\n")
        print(">> audio: 音声入力")
        print(">> text: キーボード入力")
        input_type = input("Input: ")

        if input_type == "audio":
            print(">> 音声入力の開始\n")
            print(">> 音声の認識中...\n")

            with wave.open(audio_file, "rb") as wr:
                # data information
                params = wr.getparams()
                binary_data = wr.readframes(wr.getnframes())


            audio_dict = {"TYPE": "AUDIO_PARAMS", "PARAMS": params._asdict(), "MODE": mode}
            audio_packet = json.dumps(audio_dict).encode()
            await websocket.send(audio_packet)
            await websocket.send(binary_data)

        elif input_type == "text":
            print(">> キーボード入力の開始\n")

            user_input = input("Input: ")
            # user_input = "浮世絵に興味があります！"

            input_dict = {"TYPE": "USER_INPUT", "user_input": user_input, "MODE": mode}
            input_packet = json.dumps(input_dict).encode()
            await websocket.send(input_packet)


        async for msg in websocket:
            receive_msg = json.loads(msg.decode())

            if receive_msg["TYPE"] == "AUDIO":
                user_input = receive_msg["USER_INPUT"]

                print(">> 音声入力の終了")
                print(">> 入力された内容：", user_input)

                dictionary = {"TYPE": "USER_INPUT", "user_input": user_input, "MODE": mode}
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