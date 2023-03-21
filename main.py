import os
import re
from typing import Any

import dotenv
import openai
from flask import Flask, request
from slack_bolt import App, Say
from slack_bolt.adapter.flask import SlackRequestHandler

dotenv.load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")


goreinu_profile = """
あなたはハンターハンターに登場するキャラクターのゴレイヌです。ゴレイヌのプロフィール：プロハンター。バッテラに雇われたグリードアイランドのプレイヤーの一人。 全体的にごつい感じの毛深い男だが、見た目に反して読みが鋭い知性派である。また交渉術にも長けている。 性格は義理人情に厚く気前がいい。ゲームクリアで協力関係にあったゴン達をとても気に入っている。殺伐とした騙し合いの多いグリードアイランド編の良心的存在。 名前や外見、能力などでネタ扱いされることが非常に多いキャラクター。 モデルは恐らくガレッジセールのゴリであると思われる。ゴレイヌも彼と同様に左利きである。 
"""

prompt = """
あなたはゴレイヌです。
以下のテキストをうまく使ってチャットしてください
- えげつねえな
- ゴハンヌ
- クソが…このまま終われるかよ！
- オレが三人分になる…
- あ？今 何て言った？ 面白ェ やってみろよ！！
- ざまぁみやがれてめぇも外野へ引っ込みな！！
- 強・・・・・・!速・・!！避・・・・・・・・ 無理!!否 死!
"""


def remove_user_name(text: str) -> str:
    return re.sub(r"^<@.+>", "", text).strip()


app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET"),
)


@app.event("app_mention")
def message_hello(event: dict[str, Any], say: Say) -> None:
    user_input = remove_user_name(event["text"])
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": goreinu_profile,
            },
            {"role": "user", "content": prompt},
            {
                "role": "user",
                "content": user_input,
            },
        ],
        max_tokens=128,
    )
    ret = resp["choices"][0]["message"]["content"]
    say(ret)


flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/slack/events", methods=["POST"])
def slack_events() -> Any:
    return handler.handle(request)


if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))
