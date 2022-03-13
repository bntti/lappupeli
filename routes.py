from uuid import uuid4
from flask import redirect, render_template, request, session
import random
from app import app
import database_service as dts

EMPTY = "Sait tyhjän lapun!"


# Functions
def check_uuid() -> None:
    if "uuid" not in session:
        session["uuid"] = uuid4()


def check_admin() -> bool:
    check_uuid()
    admin_uuid = dts.get_config()["admin_uuid"]
    return admin_uuid == session["uuid"]


def next_word() -> None:
    words = dts.get_words()
    if len(words) == 0:
        return

    players = dts.get_config()["players"]
    dts.clear_player_words()

    r = random.randint(1, 10)
    next_word, suggester_uuid = dts.pop_word() if r != 1 else (EMPTY, None)

    for _ in range(players - 2):
        dts.add_to_player_list(next_word)
    dts.add_to_player_list(EMPTY)
    dts.next_word(next_word, suggester_uuid)


def get_word() -> str:
    config = dts.get_config()

    if dts.has_word(session["uuid"]):
        return dts.get_word(session["uuid"])
    if session["uuid"] == config["suggester_uuid"]:
        dts.add_suggester_to_player_list(
            config["current_word"], config["suggester_uuid"]
        )
        return config["current_word"]
    if dts.get_player_list_size() == 0:
        return "Ei lappuja jäljellä"
    if dts.get_player_list_size() - dts.get_seen_count() == 0:
        return f"Lappuja on jo jaettu {config['players']} kpl"

    dts.give_word(session["uuid"])
    return dts.get_word(session["uuid"])


def clear() -> None:
    dts.clear_tables()


# Routes
@app.route("/", methods=["GET"])
def index_get() -> str:
    check_uuid()
    new = not dts.has_word(session["uuid"]) and dts.get_player_list_size() > 0
    return render_template(
        "index.html",
        words=dts.get_words(),
        config=dts.get_config(),
        seen_count=dts.get_seen_count(),
        no_words=dts.get_player_list_size() == 0,
        new=new,
        admin=check_admin()
    )


@app.route("/", methods=["POST"])
def index_post() -> str:
    check_uuid()
    if request.form.get("word"):
        dts.add_word(request.form.get("word"), session["uuid"])
    if request.form.get("players"):
        dts.set_players(int(request.form.get("players")))
    if request.form.get("be_admin"):
        dts.set_admin_uuid(session["uuid"])
    if request.form.get("unbe_admin") and check_admin():
        dts.set_admin_uuid(None)
    if request.form.get("next_word") and check_admin():
        next_word()
    if request.form.get("clear") and check_admin():
        clear()
    return index_get()


@app.route("/word")
def word() -> str:
    check_uuid()
    return render_template("word.html", word=get_word())
