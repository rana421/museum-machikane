# 方法2.5：質問文を元chatgptがQueryを作成＆ベクトルデータベースの検索(谷口改変)　それなりに動きました
#!pip install openai[embeddings]

import openai
from openai.embeddings_utils import cosine_similarity
import os,json
os.chdir(os.path.dirname(os.path.abspath(__file__))) #カレントディレクトリを固定

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY




class Search_database():

    def __init__(self):

        self.model = "gpt-3.5-turbo"


        # データベースの読み込み
        self.INDEX =None
        self.QUERY = None
        self.user_input = None
        self.exhibition_count = 5

        with open('../database/embedding.json') as f:
            self.INDEX = json.load(f)

        
        self.init_role_describe = """あなたは優秀な検索エンジンです。あなたはユーザーからの入力を元に、博物館内の展示を探す必要があります。そのための検索用の単語を出力しなくてはいけません。
        出力は単語のみを出力してください。説明文などは必要ありません。各単語を","で区切って出力してください。
        """
        self.message = None


    def make_QUERY(self,user_input):

        user_input = user_input
        self.user_input = user_input
        init_role_describe = self.init_role_describe

        message = f"""「{user_input}」
        というユーザーからの文章を元に展示を調べなくてはいけません。
        検索するための単語を、複数個あげてください。10~20個ほどあればよいでしょう。
        とにかく関連しそうなワードを挙げてください。ワードは,で区切って出力してください。
        このユーザーがどんなものが好きそうなのか、想像してみてください。
        """

        self.message  = message

        messages = [
            {"role": "system", "content": init_role_describe},
            {"role": "user", "content": message}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )

        # これが検索用の文字列
        QUERY  = response.choices[0]["message"]["content"].strip()
        self.QUERY = QUERY
        splited_query = QUERY.split(",")
        print(splited_query)
        return splited_query


    def make_output(self):


        # 検索用の文字列をベクトル化
        query = openai.Embedding.create(
            model='text-embedding-ada-002',
            input=self.QUERY
        )

        query = query['data'][0]['embedding']

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
            self.INDEX
        )
        # コサイン類似度で降順（大きい順）にソート
        results = sorted(results, key=lambda i: i['similarity'], reverse=True)

        # 以下で結果を表示
        print(f"User_Input: {self.user_input}")
        print(f"Query: {self.QUERY}")
        print("Rank: Title Similarity")
        top_suggested_museums = ""
        for i, result in enumerate(results[:self.exhibition_count]):
            print(f'{i+1}: {result["number"]}  {result["raw"][1]} {result["raw"][0]}  {result["name"]} {result["similarity"]}')

        # print("====Best Doc====")
        # print(f'number: {results[0]["number"]}')
        # print(f'name: {results[0]["name"]}')

        # print("====Worst Doc====")
        # print(f'number: {results[-1]["number"]}')
        # print(f'name: {results[-1]["name"]}')

        exhibition_text = "\n".join([f"{index+1}. " + exhibition["embedding_text"] for index, exhibition in enumerate(results[:self.exhibition_count])])
        #exhibition_text = "\n".join([f"{index+1}. " + exhibition["raw"][1] + " "+exhibition["raw"][0] + " "+exhibition["name"] for index, exhibition in enumerate(results[:exhibition_count])])
        third_msg = f"""
        上記のキーワードをもとに検索した結果、以下の{self.exhibition_count}個の展示が検索エンジンから提案されました。
        {exhibition_text}
        この{self.exhibition_count}個の展示からひとつユーザーに対して提案しようと思うのですが、
        これらの情報とユーザーからの入力をもとに、ユーザーの入力に対してフレンドリーな返答をしてください。
        ユーザーの考えを読み取り、ユーザーが聞いて楽しいような返答を心がけてください。
        出力は以下の形式で行ってください。
        {{
            "exhibition_number": {{展示番号}},
            "exhibition_name": {{展示名}},
            "exhibition_reason": {{その展示を選んだ理由}}
        }}
        """

        print(third_msg)
        messages = [
            {"role": "system", "content": self.init_role_describe},
            {"role": "user", "content": self.message},
            {"role":"assistant","content":self.QUERY},
            {"role": "user", "content": third_msg}
        ]

        response = openai.ChatCompletion.create(
            model=self.model,
            messages=messages
        )

        # 最終的な出力
        gpt_answer  = response.choices[0]["message"]["content"].strip()
        dictionary = json.loads(gpt_answer)
        print(gpt_answer)
        exhibition_reason = dictionary["exhibition_reason"]
        
        exhibition_number = dictionary["exhibition_number"]
        best_exhibition = results[int(exhibition_number) -1]
        index_num  = best_exhibition["number"]
        prefecture = best_exhibition["raw"][1]
        museum_name  = best_exhibition["raw"][0]
        exhibition_name = best_exhibition["name"]

        print("_________________________________________________________________________")
        print("{} {} {} {}".format(index_num, prefecture ,museum_name ,exhibition_name))
        print(exhibition_reason)
        return index_num, prefecture, museum_name, exhibition_name, exhibition_reason

if __name__ == "__main__":

    SDB  = Search_database()

    SDB.make_QUERY("ドラえもんに会いたいです！")
    SDB.make_output()