#import asyncio
from flask import  Flask, render_template, request
#import websocket_js
# Flaskオブジェクトの生成 --- (*1)
app = Flask(__name__,static_folder='./static')

i =0
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



@app.route("/test",methods =["GET"])
def test():
    return yojizyukugo.RandomSend()



def Start():

    app.run(debug=True,port=80,host='0.0.0.0',use_reloader=False, threaded=False)


if __name__ =="__main__":
    Start()