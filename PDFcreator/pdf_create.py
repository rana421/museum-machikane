import qrcode
import random, json
import time
from reportlab.lib.pagesizes import B5
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Flowable,Table
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader


import sys
sys.path.append('../PDFcreator')
from for_emoji import format_text_with_emoji_font
# まちかね祭全体であたり10個
# 一日の上限をもけるとしたら、3個・3個・4個とか
# MAX_HIT_COUNT = 3, PROBABILITY = 0.1
MAX_HIT_COUNT = 10
PROBABILITY = 0.1

url_path = "./image/qr.png"
backgpund_path = "./image/material_201006_01_white.png"
backgpund_rote_path = "./image/material_201006_01_white_rotate.png"
logo_path = "./image/museum_club_logo2.png"
sealing_path = "./image/sealing.png"
hit_path = "./image/hit.png"

#絵文字使用用
font_name = "Noto_Sans_JP"
font_path = "./font/Noto_Sans_JP/NotoSansJP-VariableFont_wght.ttf"

font_emoji_name = "NotoEmoji"
font_emoji_path = "./font/Noto_Emoji/NotoEmoji-VariableFont_wght.ttf"


# font_name = "genshingothic"
# font_path = "./font/genshingothic-20150607/GenShinGothic-Normal.ttf"

font_mintyou_name = "BIZ_UDMincho-Regular"
font_mintyou_path = "./font/BIZ_UDMincho/BIZUDMincho-Regular.ttf"



x_qr_path = "./image/qr_x.png"
instagram_qr_path = "./image/qr_insta.png"


# A4でのデフォルトの余白は1 inch
left_margin = 0.75 * inch
right_margin = 0.75 * inch

text_wide_point = B5[0]-left_margin-right_margin
text_height_point = B5[1]-inch-inch

# フォントの登録
pdfmetrics.registerFont(TTFont(font_name, font_path))
pdfmetrics.registerFont(TTFont(font_emoji_name, font_emoji_path))
pdfmetrics.registerFont(TTFont(font_mintyou_name, font_mintyou_path))

global_user_input = "" #globalにこれがないと動かなかった

class LineDrawing(Flowable):
    """線を描画するためのFlowableクラス"""

    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        """ページに線を描画します"""
        self.canv.setStrokeColor(black)
        self.canv.setLineWidth(1)
        self.canv.line(0, 0, self.width, 0)

from reportlab.platypus import Flowable

class ClickableImage(Flowable):
    """Clickable Image Flowable"""

    def __init__(self, image_path, url, width, height):
        super().__init__()
        self.image_path = image_path
        self.url = url
        self.width = width
        self.height = height
        self.hAlign = 'CENTER'  # アライメントを中央に設定
        # print(f"{self.height=}")
    def draw(self):
        # 画像を(0,0)に描画
        self.canv.drawImage(self.image_path, 0, 0, width=self.width, height=self.height)
        # 画像と同じ領域にリンクを設定
        self.canv.linkURL(self.url, (0, 0, self.width, self.height), relative=1)


def get_style(font_name, font_size, leading, alignment=TA_CENTER):
    return ParagraphStyle(
        "CenteredStyle",
        fontName=font_name,
        fontSize=font_size,
        leading=leading,
        alignment=alignment
    )

def create_PDF(user_input, museum_name, exhibition_name, chatgpt_response, url, is_kansai):
    global global_user_input
    global_user_input = user_input
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

        # SNSのQRコードの配置
        sns_qr_size = 60
        x_init = 70
        center_x = B5[0] // 2 - sns_qr_size - x_init
        # Twitter QRコードを描画し、そのリンクを設定
        twitter_qr_x = x_init
        twitter_qr_y = 20
        canvas.drawImage(x_qr_path, x_init, 20, width=sns_qr_size, height=sns_qr_size) #Xを描写
        canvas.linkURL("https://x.com/HA_Museumclub", (twitter_qr_x, twitter_qr_y, twitter_qr_x + sns_qr_size, twitter_qr_y + sns_qr_size))

        print(x_init+sns_qr_size+center_x*2)
        canvas.drawImage(instagram_qr_path, x_init+sns_qr_size+center_x*2, 20, width=sns_qr_size, height=sns_qr_size) #Instagramを描写
        instagram_qr_x = x_init + sns_qr_size + center_x * 2
        instagram_qr_y = 20
        canvas.linkURL("https://www.instagram.com/handai_museumclub/", (instagram_qr_x, instagram_qr_y, instagram_qr_x + sns_qr_size, instagram_qr_y + sns_qr_size))

        with open("./hit_count.json", "r") as f:
            hit_count = json.load(f)["count"]
            print(">> hit_count:", hit_count)

        # 当選機能の追加 当選の場合はシーリングスタンプを押す
        if random.random() < PROBABILITY and hit_count < MAX_HIT_COUNT:
            canvas.saveState()
            canvas.translate(B5[0] // 2 - 30, B5[1] - 85)
            canvas.rotate(0)
            canvas.drawImage(hit_path, 0, 0, width=60, height=60)
            canvas.restoreState()
            hit_count += 1
            with open("./hit_count.json", "w") as f:
                json.dump({"count": hit_count}, f)
        else:
            # シーリングスタンプの配置
            canvas.saveState()
            canvas.translate(B5[0] // 2 - 30, B5[1] - 85)
            canvas.rotate(0)
            canvas.drawImage(sealing_path, 0, 0, width=60, height=60)
            canvas.restoreState()

    def create_story(chatgpt_response,size_ration=1):
        print(">> size_ration:", size_ration)
        story = []
        story.append(Spacer(1, 20))

        global global_user_input
        user_input = format_text_with_emoji_font(global_user_input)

        if user_input == "おまかせでお願いします。なにか面白い展示を教えてください。":
            user_input = "おまかせ"
        if is_kansai:
            story.append(Paragraph("「"+user_input+"」in 関西", get_style(font_name, 20*size_ration, 30*size_ration)))
        else:
            story.append(Paragraph("「"+user_input+"」in 全国", get_style(font_name, 20*size_ration, 30*size_ration)))

        story.append(Paragraph("と入力したあなたへのおすすめは...", get_style(font_name, 15*size_ration, 30*size_ration)))

        story.append(Spacer(1, 10))

        story.append(LineDrawing(5.16 * inch, 2))
        story.append(Spacer(1, 1))
        story.append(LineDrawing(5.16 * inch, 2))

        story.append(Spacer(1, 10))

        story.append(Paragraph(museum_name, get_style(font_mintyou_name, 30*size_ration, 30*size_ration)))

        story.append(Spacer(1, 20))

        story.append(Paragraph(exhibition_name, get_style(font_mintyou_name, 30*size_ration, 30*size_ration)))

        story.append(Spacer(1, 10))

        story.append(LineDrawing(5.16 * inch, 2))
        story.append(Spacer(1, 1))
        story.append(LineDrawing(5.16 * inch, 2))

        story.append(Spacer(1, 20))

        story.append(Paragraph("同好会botからの一言", get_style(font_name, 15*size_ration, 15*size_ration, alignment=TA_LEFT)))
        story.append(Spacer(1, 20))

        chatgpt_response = format_text_with_emoji_font(chatgpt_response) #絵文字が入っている場合
        story.append(Paragraph(chatgpt_response, get_style(font_name, 15*size_ration, 20*size_ration, alignment=TA_LEFT)))

        story.append(Spacer(1, 10))

        # QRコードの設定
        qr = qrcode.QRCode(
            version=2,  # QRコードのバージョン(1~40)
            error_correction=qrcode.constants.ERROR_CORRECT_H  # 誤り訂正レベル
        )
        qr.add_data(url)
        qr.make()
        img = qr.make_image()
        img.save(url_path)

        # ClickableImageの作成
        clickable_qr = ClickableImage(url_path, url, width=100*size_ration, height=100*size_ration)

        # FlowableにhAlignプロパティを設定して中央揃え
        story.append(clickable_qr)

        story.append(Paragraph('QRコードをクリック！', get_style(font_name, 10*size_ration, 10*size_ration)))

        # 高さ計算の修正
        sum_height = 0
        for x in story:
            if isinstance(x, Paragraph):
                text_len = len(x.text.replace('<font name="NotoEmoji">',"").replace('</font>',"")) #htmlの要素部分を排除して計算する
                font_size = x.style.fontSize
                leading = x.style.leading
                # 行数の概算
                num_lines = max(1, text_len * font_size / text_wide_point)
                height = num_lines * leading
            elif isinstance(x, (Image, ClickableImage)):
                height = x.height*2 #*2をすることで収まるようになった。理由は不明である
                print(f"{height=}")
            elif isinstance(x, Table):
                # Tableのwrapメソッドを使用して高さを取得
                _, height = x.wrap(text_wide_point, 0)
            elif hasattr(x, 'height'):
                height = x.height
            else:
                height = 0
            sum_height += height

        if sum_height > text_height_point:
            print(">> sum_height:", sum_height)
            print(">> sum_height > text_height_point")
            print(">> retry")
            return create_story(chatgpt_response,size_ration=size_ration * 0.95)
        else:
            return story


    random.randint(1,100)
    doc_name = f"{time.time()}.pdf"
    doc = SimpleDocTemplate(
        # f"flask_pdf/static/{time.time()}.pdf",
        f"../PDFcreator/flask_pdf/static/{doc_name}",
        pagesize=B5,
        leftMargin=left_margin,
        rightMargin=right_margin
    )

    story = create_story(chatgpt_response)

    # ドキュメントに追加
    doc.build(story, onFirstPage=background_image, onLaterPages=background_image) #同じものが2ページ描写されるのか？よくわからん
    return doc_name

if __name__ == "__main__":
    user_input = "漫画が好きなので、漫画に関連した展示を見たい"
    museum_name = "青山剛昌ふるさと館"
    exhibition_name = "常設展"
    chatgpt_response = "わあ、漫画がお好きなんですね！それなら、青山剛昌ふるさと館の常設展がぴったりかもしれません♪\n青山剛昌さんといえば、 「名探偵コナン」の原作者として有名ですよね。漫画に興味があるあなたにぜひ見ていただきたいと思います。\n展示期間は、2023年の1月1日から12月31日までなので、ゆっくりとご覧いただけますよ。まさに、あなたのためのスペシャルな場所がここにはありますよ！\nどうでしょうか？心がワクワクするような展示ですよね！楽しい体験が待っていますよ♪"
    url = "https://www.nakamuseum.jp/exhibition/2021/2021_09_10.html"
    is_kansai = False
    create_PDF(user_input, museum_name, exhibition_name, chatgpt_response, url, is_kansai)

