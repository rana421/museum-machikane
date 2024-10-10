#appを起動させる
# import os
# print(f"{os.getcwd()=}")
import sys
sys.path.append('../')
import threading

def start_app():
    import PDFcreator.flask_pdf.app 
thread1 = threading.Thread(target=start_app)

# スレッドの処理を開始
thread1.start()

