from flask import render_template, request
import random
from app import app

players = 0
words = []
wordlist = []


@app.route("/", methods=["GET"])
def index_get() -> str:
    return render_template("index.html", words=words, players=players)


@app.route("/", methods=["POST"])
def index_post() -> str:
    global words, players
    if request.form.get("word"):
        words.append(request.form.get("word"))
    players = int(request.form.get("players"))
    return index_get()


@app.route("/word")
def word() -> str:
    global words, wordlist
    print(f"1 {players=} {words=} {wordlist=}")
    if len(wordlist) == 0:
        if len(words) == 0:
            return render_template("word.html", word="Ei sanoja jäljellä")
        word = random.choice(words)
        words.remove(word)

        wordlist = [word for _ in range(players - 1)]
        wordlist.append("Sinä sait tyhjän kortin")
        random.shuffle(wordlist)

    print(f"2 {players=} {words=} {wordlist=}")
    word = wordlist[0]
    wordlist.pop(0)
    print(f"3 {players=} {words=} {wordlist=}")
    return render_template("word.html", word=word)
