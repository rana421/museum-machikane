import qrcode
import random, json

from reportlab.lib.pagesizes import B5
from reportlab.lib.units import cm, inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Flowable
from reportlab.lib.colors import black
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# まちかね祭全体であたり10個
# 一日の上限をもけるとしたら、3個・3個・4個とか
# MAX_HIT_COUNT = 3, PROBABILITY = 0.1
MAX_HIT_COUNT = 3
PROBABILITY = 0.5

url_path = "./image/qr.png"
backgpund_path = "./image/material_201006_01_white.png"
backgpund_rote_path = "./image/material_201006_01_white_rotate.png"
logo_path = "./image/logo.png"
sealing_path = "./image/sealing.png"
hit_path = "./image/hit.png"

font_name = "genshingothic"
font_path = "./font/genshingothic-20150607/GenShinGothic-Normal.ttf"

font_mintyou_name = "BIZ_UDMincho-Regular"
font_mintyou_path = "./font/BIZ_UDMincho/BIZUDMincho-Regular.ttf"

x_qr_path = "./image/qr_x.png"
instagram_qr_path = "./image/qr_insta.png"


# B5でのデフォルトの余白は1 inch
left_margin = 0.75 * inch
right_margin = 0.75 * inch

text_wide_point = B5[0]-left_margin-right_margin
text_height_point = B5[1]-inch-inch

# フォントの登録
pdfmetrics.registerFont(TTFont(font_name, font_path))
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
        canvas.drawImage(x_qr_path, x_init, 20, width=sns_qr_size, height=sns_qr_size)
        print(x_init+sns_qr_size+center_x*2)
        canvas.drawImage(instagram_qr_path, x_init+sns_qr_size+center_x*2, 20, width=sns_qr_size, height=sns_qr_size)


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


    def create_story(size_ration=1):
        print(">> size_ration:", size_ration)
        story = []
        story.append(Spacer(1, 20))

        global global_user_input
        user_input =global_user_input
        
        if user_input== "おまかせでお願いします。なにか面白い展示を教えてください。":
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


        story.append(Paragraph(chatgpt_response, get_style(font_name, 15*size_ration, 20*size_ration, alignment=TA_LEFT)))

        story.append(Spacer(1, 10))

        #QRコードの設定
        qr = qrcode.QRCode(
            version=2, #QRコードのバージョン(1~40)
            error_correction=qrcode.constants.ERROR_CORRECT_H #誤り訂正レベル(L：約7%,M：約15%,Q:約25%,H:約30%)
        )
        qr.add_data(url)
        qr.make()
        img = qr.make_image()
        img.save(url_path)

        story.append(Image(url_path, width=100*size_ration, height=100*size_ration))
        story.append(Paragraph("展示url", get_style(font_name, 10*size_ration, 10*size_ration)))

        sum_height = 0
        for x in story:
            if x.__class__.__name__ == "Paragraph":
                text_len = len(x.frags[0].text)
                font_size = x.frags[0].fontSize
                leading = x.style.leading
                height = ((font_size * text_len // text_wide_point) + 1) * font_size + leading

            elif x.__class__.__name__ == "Image":
                height = story[-2]._height

            else:
                height = x.height
            sum_height += height

        if sum_height > text_height_point:
            print(">> sum_height:", sum_height)
            print(">> sum_height > text_height_point")
            print(">> retry")
            return create_story(size_ration=size_ration * 0.95)
        else:
            return story

    random.randint(1,100)
    doc = SimpleDocTemplate(
        "sample.pdf",
        pagesize=B5,
        leftMargin=left_margin,
        rightMargin=right_margin
    )

    story = create_story()

    # ドキュメントに追加
    doc.build(story, onFirstPage=background_image, onLaterPages=background_image)


if __name__ == "__main__":
    user_input = "漫画が好きなので、漫画に関連した展示を見たい"
    museum_name = "青山剛昌ふるさと館"
    exhibition_name = "常設展"
    chatgpt_response = "わあ、漫画がお好きなんですね！それなら、青山剛昌ふるさと館の常設展がぴったりかもしれません♪\n青山剛昌さんといえば、 「名探偵コナン」の原作者として有名ですよね。漫画に興味があるあなたにぜひ見ていただきたいと思います。\n展示期間は、2023年の1月1日から12月31日までなので、ゆっくりとご覧いただけますよ。まさに、あなたのためのスペシャルな場所がここにはありますよ！\nどうでしょうか？心がワクワクするような展示ですよね！楽しい体験が待っていますよ♪"
    url = "https://www.nakamuseum.jp/exhibition/2021/2021_09_10.html"
    is_kansai = False
    create_PDF(user_input, museum_name, exhibition_name, chatgpt_response, url, is_kansai)
