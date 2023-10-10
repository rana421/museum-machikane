#これはunityとpythonをwebsocketで相互通信するためのクラスです

import json
import websockets
import asyncio
import random
import numpy as np


class Unity_Env:
    def __init__(self):
        self.W=50
        self.H=50
        self.visual_data =np.zeros((self.W, self.H))
        self.vision_list = []
        self.experiment_list =[]
        self.experiment ={"action":{""},"vision":""}
        self.v_count =0
    
    def start(self,my_ip_addr="0.0.0.0",port=9999):

        start_server = websockets.serve(self.accept,my_ip_addr,port)
        # 非同期でサーバを待機する。
        print("start_server")
        asyncio.get_event_loop().run_until_complete(start_server)
        #get_event_loopはノンブロッキングなスレッドらしい
        asyncio.get_event_loop().run_forever()


    async def accept(websocket,self):
        while True:
            
            data = await websocket.recv()
            data = json.loads(data)
            neuron_data ={}

            for data in data.values():
                self.visual_data[data["x"]][data["y"]] = data["value"]
                #neuron_data[(data["x"],data["y"])] = data["value"]
                #heatmap_list[data["x"]][data["y"]] =data["value"]

            self.vision_list.append(self.visual_data)

            for data in neuron_data.values():
                sigma+= data
            
            print(len(self.vision_list))
            new_response = {"rotation":random.uniform(-1,1), "velocity":random.uniform(-10,10)}
            new_response = json.dumps(new_response)#このままでもエンコードされてるっぽい, encode("UTF-8")は不要？そもそもencodeするとbyteになるからいらない！！！！
            #dump関数は、ファイルとして保存するための関数で、dumps関数はエンコード(辞書型を文字列に変換)するための関数
            await websocket.send(new_response)

    def step(self):
        
env = Unity_Env()
env.start()