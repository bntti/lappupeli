from flask import redirect, render_template, request
import random
from app import app
from database import database


def get_words():
    sql = "SELECT word FROM words"
    return [a[0] for a in database.session.execute(sql).fetchall()]


def add_word_to_words(word):
    try:
        sql = "INSERT INTO words (word) VALUES (:word)"
        database.session.execute(sql, {"word": word})
        database.session.commit()
    except:
        database.session.rollback()


def word_list_pop():
    sql = "DELETE FROM words WHERE id = (SELECT id FROM words LIMIT 1) RETURNING word"
    word = database.session.execute(sql).fetchone()[0]
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
    sql = "DELETE FROM player_words WHERE id = (SELECT id FROM player_words LIMIT 1) RETURNING word"
    word = database.session.execute(sql).fetchone()[0]
    database.session.commit()
    return word


@app.route("/", methods=["GET"])
def index_get() -> str:
    return render_template("index.html", words=get_words(), players=get_players(), player_words=get_player_words())


@app.route("/", methods=["POST"])
def index_post() -> str:
    if request.form.get("word"):
        add_word_to_words(request.form.get("word"))
    if int(request.form.get("players")) != get_players():
        set_players(int(request.form.get("players")))
    return index_get()


@app.route("/word")
def word() -> str:
    player_words = get_player_words()
    if len(player_words) == 0:
        return render_template("word.html", word="Sanat loppuivat")

    word = player_list_pop()
    return render_template("word.html", word=word)


@app.route("/start")
def start() -> str:
    players = get_players()
    words = get_words()
    player_words = get_player_words()

    if len(player_words) == 0:
        if len(words) == 0:
            return redirect('/')
        r = random.randint(1, 10)
        if r == 0:
            for _ in range(players):
                add_to_player_list("Sinä sait tyhjän kortin! GLHF")
        else:
            word = word_list_pop()
            list = [word for _ in range(players - 1)]
            if r == 1:
                list.pop(0)
                list.pop(0)
                list.append("Kouvola")
                list.append("Neuvostoliitto")
            list.append("Sinä sait tyhjän kortin! GLHF")
            random.shuffle(list)
            for word in list:
                add_to_player_list(word)
    return redirect('/')


@app.route("/clear")
def clear():
    sql = "DELETE FROM words"
    database.session.execute(sql)
    sql = "DELETE FROM player_words"
    database.session.execute(sql)
    database.session.commit()
    return redirect('/')
