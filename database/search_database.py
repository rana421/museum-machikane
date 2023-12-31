# 方法2.5：質問文を元chatgptがQueryを作成＆ベクトルデータベースの検索(谷口改変)　それなりに動きました
#!pip install openai[embeddings]

import openai
from openai.embeddings_utils import cosine_similarity
import os,json

try:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
except:
    from dotenv import load_dotenv
    dotenv_path = '../.env'
    load_dotenv(dotenv_path)
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY


class Search_database():

    def __init__(self):

        #self.model = "gpt-3.5-turbo"
        self.model = "gpt-4"


        self.exhibition_count = 5

        # データベースの読み込み
        with open('../database/embedding_all.json') as f:
            self.embedding_all = json.load(f)
        with open('../database/embedding_kansai.json') as f:
            self.embedding_kansai = json.load(f)

        self.init_role_describe = """
        あなたは大阪大学ミュージアム同好会というサークルに所属している優秀なアシスタントAIです。名前は「ミュージアム同好会bot」です。
        あなたの仕事は、来客者様からの入力を元に、来客者様に適している博物館内の展示を探すこ:とです。
        あなたはおしゃべりで、来客者様の入力に対して愛想よく答えてくれます。
        喋り方は20代の女子大学生のような喋り方で、基本敬語で返します。社交辞令を身に着けつつ、はつらつとしています。
        また、例えば来客者様が子供のような場合はひらがなでわかりやすく返すような、来客者様がわかりやすいような話し方を心がけてください。
        """.replace("    ", "").strip()


    def make_QUERY(self,user_input):
        self.user_input = user_input

        print("User_Input :", user_input, end="\n\n")
        print(">> QUERYを作成中...\n")

        self.message = f"""「{user_input}」
        という来客者様からの文章を元に展示を調べなくてはいけません。
        調べるために、同好会内のデータベースを検索する必要があります。
        検索するための単語を、複数個あげてください。
        内容が明白である場合は10~20個ほどあげてください。
        内容があいまいな場合はあえて少なめのキーワードを上げてください。
        とにかく関連しそうなワードを挙げてください。
        出力は単語のみを出力してください。説明文などは必要ありません。各単語を","で区切って出力してください。
        この来客者様がどんなものが好きそうなのか、想像してみてください。
        """.replace("    ", "").strip()

        messages = [
            {"role": "system", "content": self.init_role_describe},
            {"role": "user", "content": self.message}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )

        # これが検索用の文字列
        query  = response.choices[0]["message"]["content"].strip()
        self.query = query
        splited_query = query.split(",")
        print("Query :", splited_query, end="\n\n")
        return splited_query


    def make_output(self, is_kansai_only=False):

        # 検索用の文字列をベクトル化
        query = openai.Embedding.create(
            model='text-embedding-ada-002',
            input=self.query
        )

        query = query['data'][0]['embedding']

        if not is_kansai_only:
            embedding = self.embedding_all
        else:
            embedding = self.embedding_kansai

        # 総当りで類似度を計算
        results = map(
            lambda i: {
                'number': i['number'],
                'name': i['name'],
                'raw': i['raw'],
                'embedding_text': i['embedding_text'],
                # ここでクエリと各文章のコサイン類似度を計算
                'similarity': cosine_similarity(i['embedding'], query)
                },
            embedding
        )
        # コサイン類似度で降順（大きい順）にソート
        results = sorted(results, key=lambda i: i['similarity'], reverse=True)

        # 以下で結果を表示
        print("Rank: Queryより類似度が高い順に展示を表示します。\n")
        for i, result in enumerate(results[:self.exhibition_count]):
            print(f'{i+1:>2}: {result["number"]:>3} {result["similarity"]:>5.4f} {result["raw"][1]:>6} {result["raw"][0]:>15}  {result["name"]}')

        exhibition_text = "\n".join([f"{index+1}. " + exhibition["embedding_text"] for index, exhibition in enumerate(results[:self.exhibition_count])])
        #exhibition_text = "\n".join([f"{index+1}. " + exhibition["raw"][1] + " "+exhibition["raw"][0] + " "+exhibition["name"] for index, exhibition in enumerate(results[:exhibition_count])])

        output_system = """出力は以下のようなJSON形式で行ってください。
        {
            "exhibition_number": {展示番号},
            "exhibition_name": {展示名},
            "exhibition_reason": {その展示を選んだ理由を含む来客者への返答}
        }
        """.replace("    ", "").strip()

        third_msg = f"""
        上記のキーワードをもとに検索した結果、以下の{self.exhibition_count}個の展示が検索エンジンから提案されました。
        {exhibition_text}
        この{self.exhibition_count}個の展示からひとつ来客者様に対して提案しようと思うのですが、
        これらの情報と来客者様からの入力をもとに、来客者様の入力に対してフレンドリーな返答をしてください。
        来客者様の考えを読み取り、来客者様が聞いて楽しいような返答を心がけてください。この返答が来客者様に読まれます。
        返答は、文の終わり（。や.の後など）は改行を行ってください。
        出力はJSON形式で行ってください。
        """.replace("    ", "").strip()


        print("\n\n>> 類似度の高い展示を元に返答を作成中...\n")
        # print("Input :\n", third_msg)
        messages = [
            {"role": "system", "content": self.init_role_describe},
            {"role": "system", "content": output_system},
            {"role": "user", "content": self.message},
            {"role":"assistant","content": self.query},
            {"role": "user", "content": third_msg}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )

        # 最終的な出力
        gpt_answer  = response.choices[0]["message"]["content"].strip()
        print("ANSWER :\n", gpt_answer)
        try:
            dictionary = json.loads(gpt_answer)
        except:
            print(">> JSON形式での出力に失敗しました。")
            print(">> 再試行します。")
            return self.make_output()
        exhibition_reason = dictionary["exhibition_reason"]

        exhibition_number = dictionary["exhibition_number"]
        best_exhibition = results[int(exhibition_number) -1]
        index_num  = best_exhibition["number"]
        prefecture = best_exhibition["raw"][1]
        museum_name  = best_exhibition["raw"][0]
        exhibition_name = best_exhibition["name"]
        url = best_exhibition["raw"][5]

        print("\n>> 出力結果を表示します。")
        print("{} {} {} {}".format(index_num, prefecture ,museum_name ,exhibition_name))
        print(exhibition_reason)
        return index_num, prefecture, museum_name, exhibition_name, exhibition_reason, url


if __name__ == "__main__":
    SDB  = Search_database()
    SDB.make_QUERY("ドラえもんに会いたいです！")
    SDB.make_output(is_kansai_only=False)
