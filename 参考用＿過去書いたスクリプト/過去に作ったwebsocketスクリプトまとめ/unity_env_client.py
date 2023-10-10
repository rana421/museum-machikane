import json
from websocket import create_connection #これはwebsocket-clientというライブラリ, websocketsとは違う！
import numpy as np
import matplotlib.pyplot as plt
import cv2
class Unity_Env:
    def __init__(self,port =3000):
        self.uri = "ws://localhost:" + str(port)
        self.ws = create_connection(self.uri)
        self.W=200
        self.H=200
        self.visual_data =np.zeros((self.W, self.H))
        self.vision_list = []
    
    def reset(self):
        self.ws.send("reset")
        result =  self.ws.recv()
        result = json.loads(result)
        print(result)

    def step(self,action=None):
        self.ws.send("step")
        result =  self.ws.recv()
        result = json.loads(result)
        next_state = result["next_state"]
        for i in range(0,len(result["next_state"]["value_list"])):
            x = int(result["next_state"]["x_list"][i])
            y = int(result["next_state"]["y_list"][i])
            value = result["next_state"]["value_list"][i]
            #print(f"{x}     {y}   {value}")
            self.visual_data[y][x] = value

        return self.visual_data
    
    def close(self):
        self.ws.close()

env = Unity_Env()

import time

while(True):
    # 1フレーム毎　読込み
    img = env.step()
    img = cv2.flip(img,0) #0で上下反転らしい
    img = cv2.resize(img,dsize=(500,500))

    cv2.imshow("Unity", img)
    # qキーが押されたら途中終了
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 終了処理
cv2.destroyAllWindows()