# museum-machikane
ミュージアム同好会のまちかね祭プロジェクト

python側の処理は谷口のサーバorローカルのPCで実行することになりそうです。
現状考えているのはapacheでhtmlリクエストを受理して(これはポート80)、gptやwhisperの処理はflaskを使って別ポート(8080とか？)を使うhttpリクエストからopenai系の処理をすべて１つのpythonコードで実行するかな...といった感じです。
flask_testは