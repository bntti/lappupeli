from uuid import uuid4
from flask import redirect, render_template, request, session
import random
from app import app
import database_service as dts

EMPTY = "Sait tyhjän lapun!"


def check_uuid():
    if "uuid" not in session:
        session["uuid"] = uuid4()


@app.route("/", methods=["GET"])
def index_get() -> str:
    check_uuid()
    new = not dts.has_word(session["uuid"]) and dts.get_player_list_size() > 0
    return render_template(
        "index.html",
        words=dts.get_words(),
        config=dts.get_config(),
        seen_count=dts.get_seen_count(),
        new=new
    )


@app.route("/", methods=["POST"])
def index_post() -> str:
    if request.form.get("word"):
        dts.add_word(request.form.get("word"))
    if request.form.get("players"):
        dts.set_players(int(request.form.get("players")))
    return index_get()


@app.route("/word")
def word() -> str:
    check_uuid()
    players = dts.get_config()["players"]

    if dts.has_word(session["uuid"]):
        return render_template("word.html", word=dts.get_word(session["uuid"]))
    if dts.get_player_list_size() == 0:
        return render_template("word.html", word=f"Ei lappuja jäljellä")
    elif dts.get_player_list_size() - dts.get_seen_count() == 0:
        return render_template("word.html", word=f"Lappuja on jo jaettu {players} kpl")
    else:
        dts.give_word(session["uuid"])
        return render_template("word.html", word=dts.get_word(session["uuid"]))


@app.route("/start")
def start() -> str:
    words = dts.get_words()
    if len(words) == 0:
        return redirect('/')

    players = dts.get_config()["players"]
    dts.clear_player_words()

    r = random.randint(1, 10)
    word = dts.pop_word() if r != 1 else EMPTY

    for _ in range(players - 1):
        dts.add_to_player_list(word)
    dts.add_to_player_list(EMPTY)
    dts.update_previous_word()
    dts.update_current_word(word)
    return redirect('/')


@app.route("/clear")
def clear():
    dts.clear_tables()
    return redirect('/')
