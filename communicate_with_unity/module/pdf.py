import qrcode
import random, json

from reportlab.lib.pagesizes import B5
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

global hit_count

hit_count = 0

# with open("./hit_count.json", "r") as f:
#     hit_count = json.load(f)["count"]

probability = 1
max_hit = 100

url_path = "./image/qr.png"
backgpund_path = "./image/material_201006_01_white.png"
backgpund_rote_path = "./image/material_201006_01_white_rotate.png"
logo_path = "./image/logo.png"
sealing_path = "./image/sealing.png"

font_name = "genshingothic"
font_path = "./font/genshingothic-20150607/GenShinGothic-Normal.ttf"

x_qr_path = "./image/qr_x.png"
instagram_qr_path = "./image/qr_insta.png"


def create_PDF(museum_name, exhibition_name, chatgpt_response, url):
    # フォントの登録
    pdfmetrics.registerFont(TTFont(font_name, font_path))

    # スタイルの取得
    styles = getSampleStyleSheet()

    def get_style(font_name, font_size, leading):
        return ParagraphStyle(
            "CenteredStyle",
            fontName=font_name,
            fontSize=font_size,
            leading=leading,
            alignment=TA_CENTER
        )

    def background_image(canvas, doc):
        img_width, img_height = 100, 100
        # translateとrotateの関係で、左上、左下、右上、右下の順に画像を配置する

        # 左上
        canvas.saveState()
        canvas.translate(0, B5[1] - img_height)
        canvas.rotate(0)
        canvas.drawImage(backgpund_path, 0, 0, width=img_width, height=img_height)
        canvas.restoreState()

        # 左下
        canvas.saveState()
        canvas.translate(img_width, 0)
        canvas.rotate(90)
        canvas.drawImage(backgpund_path, 0, 0, width=img_width, height=img_height)
        canvas.restoreState()

        # 右上
        canvas.saveState()
        canvas.translate(B5[0] - img_width, B5[1])
        canvas.rotate(-90)
        canvas.drawImage(backgpund_path, 0, 0, width=img_width, height=img_height)
        canvas.restoreState()

        # 右下
        canvas.saveState()
        canvas.translate(B5[0], img_width)
        canvas.rotate(180)
        canvas.drawImage(backgpund_path, 0, 0, width=img_width, height=img_height)
        canvas.restoreState()


        # logoの配置
        # どこに配置するかは考える必要がある
        canvas.saveState()
        canvas.translate(0, 0)
        canvas.drawImage(logo_path, (B5[0]-58.26*3) // 2, 10, width=58.26*3, height=28.74*3)
        canvas.restoreState()

        # シーリングスタンプの配置
        canvas.saveState()
        canvas.translate(60, B5[1] - 180)
        canvas.rotate(30)
        canvas.drawImage(sealing_path, 0, 0, width=75, height=75)
        canvas.restoreState()


        # 当選機能の追加 当選の場合はシーリングスタンプを押す
        if random.random() < probability and hit_count < max_hit:
            canvas.saveState()
            canvas.translate(420, B5[1] - 180)
            canvas.rotate(30)
            canvas.drawImage(sealing_path, 0, 0, width=75, height=75)
            canvas.restoreState()
            # hit_count += 1
            # with open("./hit_count.json", "w") as f:
            #     json.dump({"count": hit_count}, f)


    story = []
    doc = SimpleDocTemplate("sample.pdf", pagesize=B5)

    story.append(Paragraph("あなたへのおすすめは...", get_style(font_name, 20, 20)))

    story.append(Spacer(1, 20))

    story.append(Paragraph(museum_name, get_style(font_name, 30, 30)))

    story.append(Spacer(1, 40))

    story.append(Paragraph(exhibition_name, get_style(font_name, 30, 30)))

    story.append(Spacer(1, 30))

    story.append(Paragraph(chatgpt_response, get_style(font_name, 10, 15)))

    story.append(Spacer(1, 20))

    #QRコードの設定
    qr = qrcode.QRCode(
        version=2, #QRコードのバージョン(1~40)
        error_correction=qrcode.constants.ERROR_CORRECT_H #誤り訂正レベル(L：約7%,M：約15%,Q:約25%,H:約30%)
    )
    qr.add_data(url)
    qr.make()
    img = qr.make_image()
    img.save(url_path)

    # 展示url, twitter, instagramのqrを配置

    # 3つの画像とテキストのリストを作成します
    image_paths = [url_path, x_qr_path, instagram_qr_path]
    image_captions = ["展示url", "X(twitter)", "instagram"]

    # Image オブジェクトのリストと、それに対応するキャプションのリストを作成します
    images = [Image(img_path, width=4*cm, height=4*cm) for img_path in image_paths]
    styles = getSampleStyleSheet()
    captions = [Paragraph(text, get_style(font_name, 10, 10)) for text in image_captions]

    # Table を使って画像とキャプションを配置します
    data = [images, captions]
    table = Table(data, colWidths=[4.5*cm]*3)

    story.append(table)

    # ドキュメントに追加
    doc.build(story, onFirstPage=background_image, onLaterPages=background_image)


if __name__ == "__main__":
    museum_name = "公益財団法人中野美術館"
    exhibition_name = "近代の日本画〈日本画展示室〉"
    chatgpt_response = "浮世絵に興味がおありとのことですが、近代の日本画展示室では富岡鉄斎や横山大観などの著名な日本画家の作品を展示しています。彼らの作品は 浮世絵とはまた異なる美しさや表現方法を持っており、日本の伝統に根ざした芸術の魅力を感じることができます。ぜひ、この展示をご覧いただき 、日本画の魅力に触れてみてください。展示は2023年9月10日から11月13日まで開催されています。お楽しみに！"
    url = "https://www.nakamuseum.jp/exhibition/2021/2021_09_10.html"
    create_PDF(museum_name, exhibition_name, chatgpt_response, url)