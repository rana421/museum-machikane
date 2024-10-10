from flask import Flask, render_template, send_from_directory, abort
import os

app = Flask(__name__)

# PDFファイルが配置されているディレクトリ
PDF_DIRECTORY = os.path.join(app.root_path, 'static')

# @app.route('/')
# def index():
#     # index.htmlテンプレートをレンダリング
#     return render_template('index.html')

@app.route('/pdf/<filename>')
def serve_pdf(filename):
    try:
        # 安全にファイルパスを結合
        print(f"{filename=}")
        return send_from_directory(PDF_DIRECTORY, filename, as_attachment=False)
        #as_attachment=Falseに設定することで、ブラウザ上でPDFを直接表示します。Trueにするとダウンロードが促されます
    except FileNotFoundError:
        abort(404)

# print(f"{__name__=}")
if __name__ == '__main__' or __name__ == 'PDFcreator.flask_pdf.app':
    #このコードを直接動作させた時または__init__.pyからimportされたときのみに動作する
    app.run(host="0.0.0.0",port="80",debug=True)
    print("flask is active!")
