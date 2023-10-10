import asyncio
import json
from time import time
import websockets
import nest_asyncio
nest_asyncio.apply() #これをするだけでasyncioが使えるようになる！！！すごい！！！
import threading
from flask import  Flask, render_template, request
import yojizyukugo



room_dict ={}

app = Flask(__name__,static_folder='./static')
# ルート( / )へアクセスがあった時の処理を記述 --- (*2)
@app.route("/")
def root():
    global i
    i+=1
    return render_template("main_menu.html")
    

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/rule")
def rule():
    return render_template("rule.html")

@app.route("/get_quiz")
def get_quiz():
    return yojizyukugo.RandomSend()



@app.route("/create_room",methods =["GET"])
def create_room():
    data_dict ={}
    for data in request.query_string.decode('utf-8').split("&"):
        pair = data.split("=")
        data_dict[pair[0]] =pair[1]

    if data_dict['room_name'] in room_dict:
        return 'そのルーム名は既に使用されています！'
    
    else:
        room = room_data()
        room.password = data_dict['password']
        room.players[0]["name"]=data_dict["ID"]
        room_dict[data_dict["room_name"]] = room

        return render_template("quiz_main.html")


    #return yojizyukugo.RandomSend()


@app.route("/find_room",methods =["GET"])
def find_room():
    data_dict ={}
    for data in request.query_string.decode('utf-8').split("&"):
        pair = data.split("=")
        data_dict[pair[0]] =pair[1]
      
    for k,v in room_dict.items():
      if k==data_dict['room_name'] and v.password==data_dict['password']:
        for a in v.players:
          if a["name"] == data_dict["ID"]:
            return "ルーム内に同じ名前のプレイヤーがいます!<p>名前を変更してください</p>"
        for a in v.players:
          if a["name"] =="":
            a["name"] = data_dict["ID"]
            return render_template("quiz_main.html")
        
        return "ルーム中のプレイヤー数が上限です！"
          
        
    else:

        return 'ルーム名またはパスワードが違います！'


    #return yojizyukugo.RandomSend()





def Start():

    app.run(debug=True,port=80,host='0.0.0.0',use_reloader=False, threaded=True)

i =0
message = "preset"
data_dict ={}
change_flags = {}

class room_data:
    password =''
    players =[
      {"name" :"", "score":0,"change_flag":0,"TorF":0,"answer_num":0,"comment":"","_isExist":1,"f_for_js":0},
      {"name" :"", "score":0,"change_flag":0,"TorF":0,"answer_num":0,"comment":"","_isExist":1,"f_for_js":0},
      {"name" :"", "score":0,"change_flag":0,"TorF":0,"answer_num":0,"comment":"","_isExist":1,"f_for_js":0},
      {"name" :"", "score":0,"change_flag":0,"TorF":0,"answer_num":0,"comment":"","_isExist":1,"f_for_js":0}

    ]
    #0:name 1:score


async def recv(websocket,my_number,my_room):
  global data_dict,change_flags
  while True:
    try:
      data = await websocket.recv()
      #print(data)
      #message = data.decode()
      my_room.players[my_number] = json.loads(data) #自分のデータだけ書き換えとか
      
      a = my_room.players.copy()
      for i in range(0,4):
        #print( str(my_number)+"の"+str(i) +"回目フラッグ書き換え中")
        if i == my_number:
          continue
        else:
          my_room.players[i]["change_flag"]=1

      a.clear()
       
        

        
     
    
    except websockets.exceptions.ConnectionClosedOK:
      print("Closed")
      my_room.players[my_number]["_isExist"] = 0
      a = my_room.players.copy()
      for i in range(0,4):
        if i == my_number:
          continue
        else:
          my_room.players[i]["change_flag"]=1
      a.clear()
      break



async def send(websocket,my_number,my_room):
  #await websocket.send(str(my_number).encode())
  while True:
    try:
      if my_room.players[my_number]["change_flag"]==1:
        print(str(my_number) +"がON")
        send_data = json.dumps(my_room.players)
        await websocket.send(send_data)
        my_room.players[my_number]["change_flag"]=0

      await asyncio.sleep(0.01) #めっちゃ早くに（実際は15msくらいらしい？）
    
    except websockets.exceptions.ConnectionClosedOK:
      print("send_close")
      break

        
    


    


# クライアント接続すると呼び出す
async def accept(websocket, path):
  global i,change_flags,room_dict

  data = await websocket.recv()
  
  data_dict={}
  for data in data.split("&"):
        pair = data.split("=")
        data_dict[pair[0]] =pair[1]
  
  room_name = data_dict['room_name']
  my_id = data_dict['ID']
  password = data_dict['password']
  print(room_name+","+my_id +"," +password)
  count =0
  for k,v in room_dict.items():
    if k==room_name and v.password ==password:
      my_room =v 
      print("ルーム名は"+k +"で、辞書番号は"+ str(count)+"です")
      count+=1
    print("ルーム数は現在"+str(len(room_dict))+"です")

  for player in my_room.players:
    
    if player['name'] == my_id:
      #print(my_room.players.index(player))
      my_number=my_room.players.index(player)

  for player in my_room.players:
    '''
    if my_room.players.index(player)==my_number:
      continue
    '''
    if player['name'] != "" :
      player["change_flag"] =1 #ここでみんなに新しく参加したことを報告？

  await websocket.send(str(my_number))
  change_flags[my_number] = "0"
  loop = asyncio.get_event_loop()
  gather = asyncio.gather(recv(websocket,my_number,my_room),send(websocket,my_number,my_room))
  loop.run_until_complete(gather)


if __name__ == '__main__':
  start_server = websockets.serve(accept, "0.0.0.0", 9999)
  print('main_Start')
  sub =threading.Thread(target=Start) #flaskをサブスレッドで動作させる
  sub.start()
  print("flask_start")
 
  # 非同期でサーバを待機する。
  asyncio.get_event_loop().run_until_complete(start_server)
  #get_event_loopはノンブロッキングなスレッドらしい
  asyncio.get_event_loop().run_forever()
  
  

  

  