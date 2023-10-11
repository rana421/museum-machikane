import json
import websockets
import asyncio
import random
import numpy as np


#from __future__ import unicode_literals, print_function
from seaborn.matrix import heatmap
import matplotlib.pyplot as plt
import threading



W=50
H=50
visual_data =np.zeros((W, H))
test = np.random.rand(H,1)

vision_list = []
experiment_list =[]
experiment ={"action":{""},"vision":""}
v_count =0

async def accept(websocket, path):
    while True:
        #plt.clf()
        data = await websocket.recv()
        data = json.loads(data)
        neuron_data ={}

        for data in data.values():
            visual_data[data["x"]][data["y"]] = data["value"]
            #neuron_data[(data["x"],data["y"])] = data["value"]
            #heatmap_list[data["x"]][data["y"]] =data["value"]

        vision_list.append(visual_data)
        #print(np.dot(visual_data,test))
        #print(visual_data.shape)
        """
        v_count =0
        plt.clf()
        plt.imshow(vision_list[v_count],interpolation='nearest',vmin=0,vmax=1,cmap='gray')
        plt.pause(0.01)
        v_count =v_count+1
        """
        #vision_list.pop(v_count)

        
        
        sigma =0
        for data in neuron_data.values():
            sigma+= data
        
        print(len(vision_list))
        new_response = {"rotation":random.uniform(-1,1), "velocity":random.uniform(-10,10)}
        new_response = json.dumps(new_response)#このままでもエンコードされてるっぽい, encode("UTF-8")は不要？そもそもencodeするとbyteになるからいらない！！！！
        #dump関数は、ファイルとして保存するための関数で、dumps関数はエンコード(辞書型を文字列に変換)するための関数


        #print(new_response)
        #response = random.randint(0,3)
        await websocket.send(new_response)


start_server = websockets.serve(accept, "0.0.0.0", 9999)
# 非同期でサーバを待機する。
asyncio.get_event_loop().run_until_complete(start_server)
#get_event_loopはノンブロッキングなスレッドらしい
asyncio.get_event_loop().run_forever()
