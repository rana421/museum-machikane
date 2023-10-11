import asyncio
import json
import websockets
import nest_asyncio
nest_asyncio.apply() #これをするだけでasyncioが使えるようになる！！！すごい！！！
import threading
from flask import  Flask, render_template, request
import yojizyukugo



room_list =[]

app = Flask(__name__,static_folder='./static')
# ルート( / )へアクセスがあった時の処理を記述 --- (*2)
@app.route("/")
def root():
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
  global room_list
  data_dict ={}
  '''
  for room in room_list:
    print("ルーム名:",room.room_name,"パスワード:",room.password,"の中のplayerデータ:",room.players)
    '''
    
  for data in request.query_string.decode('utf-8').split("&"):
      pair = data.split("=")
      data_dict[pair[0]] =pair[1]

  for room in room_list:
    if room.room_name == data_dict['room_name']:
      return 'そのルーム名は既に使用されています！'

  
  room_list.append(room_data(data_dict['room_name'],data_dict['password'],data_dict["ID"]))

  return render_template("quiz_main.html")


  #return yojizyukugo.RandomSend()


@app.route("/find_room",methods =["GET"])
def find_room():
    global room_list
    data_dict ={}
    for data in request.query_string.decode('utf-8').split("&"):
        pair = data.split("=")
        data_dict[pair[0]] =pair[1]
      
    for room in room_list:
      #print(room.room_name ,"のplayers:",room.players)
      if room.room_name == data_dict['room_name'] and room.password == data_dict['password']:
        for a in room.players:
          if a["name"] == data_dict["ID"]:
            return "ルーム内に同じ名前のプレイヤーがいます!<p>名前を変更してください。</p>"
        for a in room.players:
          if a["name"] =="":
            a["name"] = data_dict["ID"]
            return render_template("quiz_main.html")
        
        return "ルーム中のプレイヤー数が上限です！"
          
        

    return 'ルーム名またはパスワードが違います！'


    #return yojizyukugo.RandomSend()





def Start():

    app.run(debug=True,port=80,host='0.0.0.0',use_reloader=False, threaded=True)






class room_data:

  def __init__(self,room_name,password,player_name):

    self.players = [
    {"name" :"", "score":0,"change_flag":0,"TorF":"","answer_num":0,"comment":"","_isExist":1,"f_for_js":0},
    {"name" :"", "score":0,"change_flag":0,"TorF":"","answer_num":0,"comment":"","_isExist":1,"f_for_js":0},
    {"name" :"", "score":0,"change_flag":0,"TorF":"","answer_num":0,"comment":"","_isExist":1,"f_for_js":0},
    {"name" :"", "score":0,"change_flag":0,"TorF":"","answer_num":0,"comment":"","_isExist":1,"f_for_js":0}

  ]
    #selfでprivate関数を表す！！！超重要！！！
    self.room_name = room_name
    self.password = password
    self.players[0]["name"] = player_name
    #print(room_name,":initialized!")



    
  def start(self,websocket,my_id):    
    for player in self.players:
      if player['name'] == my_id:
        my_index=self.players.index(player)

    loop = asyncio.get_event_loop()
    gather = asyncio.gather(self.recv(websocket,my_index),self.send(websocket,my_index))
    loop.run_until_complete(gather)


  async def send(self,websocket,my_id):
 
    for player in self.players:  
        player["change_flag"] =1 #ここでみんなに新しく参加したことを報告？
    
    await websocket.send(str(my_id))
    

    while True:
      try:
        if self.players[my_id]["change_flag"]==1:
          self.players[my_id]["change_flag"]=0
          #print(room_name+"の"+str(my_number) +"番目がONです。")
          send_data = json.dumps(self.players)
          await websocket.send(send_data)
          

        await asyncio.sleep(0.01) #めっちゃ早くに（実際は15msくらいらしい？）
      
      except websockets.exceptions.ConnectionClosedOK:
        print("send_close")
        break




  async def recv(self,websocket,my_id):


    while True:
      try:
        data = await websocket.recv()
        #print(data)
        #message = data.decode()
        self.players[my_id] = json.loads(data) #自分のデータだけ書き換えとか
        
        
        for i in range(0,4):
          #print( str(my_number)+"の"+str(i) +"回目フラッグ書き換え中")
          self.players[i]["change_flag"]=1

      
      except websockets.exceptions.ConnectionClosedOK:
        print("Closed")
        self.players[my_id]["_isExist"] = 0
        for i in range(0,4):
          if self.players[i]["_isExist"] ==1:
            break #一人でもいれば操作を続ける
          if i==3:
            room_list.pop() 

        for i in range(0,4):
          if i == my_id:
            continue
          else:
            self.players[i]["change_flag"]=1
        break






    


# クライアント接続すると呼び出す
async def accept(websocket, path):
  global room_list

  data = await websocket.recv()
  
  data_dict={}
  for data in data.split("&"):
        pair = data.split("=")
        data_dict[pair[0]] =pair[1]
  
  room_name = data_dict['room_name']
  my_id = data_dict['ID']
  password = data_dict['password']
  
 

  for room in room_list:
    #print(room.room_name ,"のplayers:",room.players)
    if room.room_name == room_name and room.password ==password:
      #print("websocket_accpt受信, ルーム名は"+room_name+",idは"+my_id +",パスワードは" +password)
      room.start(websocket,my_id)


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
  
  

  

  