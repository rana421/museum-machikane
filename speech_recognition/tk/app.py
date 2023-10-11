import tkinter as tk
import threading
import speech_recognition as sr

class VoiceToTextApp:
    def __init__(self, root):
        self.root = root
        self.root.title("音声入力リアルタイム表示")

        self.transcribed_text = tk.StringVar()
        
        self.entry = tk.Entry(self.root, textvariable=self.transcribed_text, width=50)
        self.entry.grid(row=0, column=0, padx=10, pady=10)

        self.button = tk.Button(self.root, text="音声入力開始", command=self.start_listening)
        self.button.grid(row=1, column=0, padx=10, pady=10)

    def start_listening(self):
        # スレッドを使用して、GUIがフリーズしないようにする
        threading.Thread(target=self.listen_to_voice).start()

    def listen_to_voice(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("音声入力を待機中...")
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language="ja-JP")
                self.transcribed_text.set(text)
            except sr.UnknownValueError:
                print("音声を認識できませんでした")
            except sr.RequestError as e:
                print(f"APIへのリクエストに失敗しました; {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = VoiceToTextApp(root)
    root.mainloop()