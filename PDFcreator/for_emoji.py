import emoji

import emoji

def format_text_with_emoji_font(text, emoji_font_name='NotoEmoji'):
    """
    テキストから絵文字部分を抜き出し、絵文字部分に対してのみ指定したフォントを適用したHTML形式のテキストを返します。

    Args:
        text (str): 処理対象のテキスト。
        emoji_font_name (str): 絵文字に適用するフォント名（デフォルトは 'NotoEmoji'）。

    Returns:
        str: 絵文字部分が指定フォントで囲まれたHTML形式のテキスト。
    """
    # 結果を格納するリスト
    result = []
    last_index = 0

    # 絵文字を検出し、イテレートする
    for match in emoji.emoji_list(text):
        emoji_char = match['emoji']
        start = match['match_start']
        end = start + len(emoji_char)

        # 絵文字以外の部分を追加
        if start > last_index:
            result.append(text[last_index:start])

        # 絵文字部分をフォントタグで囲む
        wrapped_emoji = f'<font name="{emoji_font_name}">{emoji_char}</font>'
        result.append(wrapped_emoji)

        last_index = end

    # 残りのテキストを追加
    if last_index < len(text):
        result.append(text[last_index:])

    # リストを結合して結果を返す
    return ''.join(result)



if __name__ == "__main__":
    sample_text = 'こんにちは！✨絵文字を使いたくなるほど楽しみな展示を見つけましたよ！😊 それは『文字の芸術をめぐる旅 文字ってアートなの？』という展示です！🖼️この展示では、文字や記号がどのようにアートとして表現されるのかを探ります。🔤 まさに絵文字のように、文字がアートとして持つ意味や美しさに注目していますよ。多様な文字を使った作品を通して、文字の新たな魅力を発見できるかも！？🎨是非、あなたのクリエイティブな感性を刺激するこの展示を楽しんでみてくださいね！🌟'
    # sample_text = 'こんにちは'
    formatted_text = format_text_with_emoji_font(sample_text)
    print(sample_text)
    print(formatted_text)
    # print(formatted_text.replace('<font name="NotoEmoji">',"").replace('</font>',""))