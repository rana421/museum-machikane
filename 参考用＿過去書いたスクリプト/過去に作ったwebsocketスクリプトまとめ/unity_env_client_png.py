import json
from websocket import create_connection #これはwebsocket-clientというライブラリ, websocketsとは違う！
import numpy as np
import matplotlib.pyplot as plt
import cv2
import time
import base64

class Unity_Env:
    def __init__(self,port =3000):
        self.uri = "ws://localhost:" + str(port)
        self.ws = create_connection(self.uri)
        self.W=200
        self.H=200
        self.visual_data =np.zeros((self.W, self.H))
        self.vision_list = []
    
    def reset(self):
        send_data = {"command": "reset"}
        send_data = json.dumps(send_data)

        self.ws.send(send_data)

        result =  self.ws.recv()
        result = json.loads(result)
        result = result["result"]
        Sensor_list = result["Sensor_Linst"]

        img = result["PNG_image"]
        img = base64.b64decode(img)
        arr = np.frombuffer(img, dtype=np.uint8)
        img = cv2.imdecode(arr, flags=cv2.IMREAD_COLOR)
        state = [img,Sensor_list]
        return state

    def step(self,action={"Fz":0, "Ry":0,"HRx":0,"HRy":0}):
        send_data = {"command": "step", "Fz":action["Fz"],"Ry":action["Ry"], "HRy":action["HRy"],"HRx":action["HRx"]}
        send_data = json.dumps(send_data)
        self.ws.send(send_data)

        result =  self.ws.recv()
        result = json.loads(result)
        result = result["result"]
        Sensor_list = result["Sensor_Linst"]
        reward = result["reward"]
        done = result["done"]
        info= result["info"]
        img = result["PNG_image"]
        img = base64.b64decode(img)
        arr = np.frombuffer(img, dtype=np.uint8)
        img = cv2.imdecode(arr, flags=cv2.IMREAD_COLOR)
        state = [img,Sensor_list]
        return state,reward,done,info
    
    def close(self):
        self.ws.close()




if __name__== "__main__":

    import random

    env = Unity_Env()

    state = env.reset()
    while(True):
        # 1フレーム毎　読込み
        state,reward,done,info = env.step(action={"Fz":30, "Ry":5,"HRx":0,"HRy":0})
        img = state[0]
        cv2.imshow("Unity", img)
        print(reward)
        # qキーが押されたら途中終了
        if cv2.waitKey(1) & 0xFF == ord('q'):
            state = env.reset()
            print(state[1])
            break

        if done:
            state = env.reset()

    # 終了処理q
    cv2.destroyAllWindows()