from flask import render_template, request
import random
from app import app
from database import database


def get_words():
    sql = "SELECT word FROM words"
    return [a[0] for a in database.session.execute(sql).fetchall()]


def set_words(word):
    sql = "INSERT INTO words (word) VALUES (:word)"
    database.session.execute(sql, {"word": word})
    database.session.commit()


def word_list_pop():
    sql = "SELECT word, id FROM words ORDER BY random() LIMIT 1"
    word, id = database.session.execute(sql).fetchone()
    sql = "DELETE FROM words WHERE id = :id"
    database.session.execute(sql, {"id": id})
    database.session.commit()
    return word


def get_player_words():
    sql = "SELECT word FROM player_words"
    return [a[0] for a in database.session.execute(sql).fetchall()]


def get_players():
    sql = "SELECT players FROM config"
    return database.session.execute(sql).fetchone()[0]


def set_players(players):
    sql = "UPDATE config SET players = :players"
    database.session.execute(sql, {"players": players})
    database.session.commit()


def add_to_player_list(word):
    sql = "INSERT INTO player_words (word) VALUES (:word)"
    database.session.execute(sql, {"word": word})
    database.session.commit()


def player_list_pop():
    sql = "SELECT word, id FROM player_words ORDER BY random() LIMIT 1"
    word, id = database.session.execute(sql).fetchone()
    sql = "DELETE FROM player_words WHERE id = :id"
    database.session.execute(sql, {"id": id})
    database.session.commit()
    return word


@app.route("/", methods=["GET"])
def index_get() -> str:
    return render_template("index.html", words=get_words(), players=get_players())


@app.route("/", methods=["POST"])
def index_post() -> str:
    if request.form.get("word"):
        set_words(request.form.get("word"))
    if int(request.form.get("players")) != get_players():
        set_players(int(request.form.get("players")))
    return index_get()


@app.route("/word")
def word() -> str:
    players = get_players()
    words = get_words()
    player_words = get_player_words()

    print(f"1 {players=} {words=} {player_words=}")
    if len(player_words) == 0:
        if len(words) == 0:
            return render_template("word.html", word="Sanat loppuivat")
        word = word_list_pop()
        for _ in range(players - 1):
            add_to_player_list(word)
        add_to_player_list("Sinä sait tyhjän kortin")

    word = player_list_pop()
    return render_template("word.html", word=word)
