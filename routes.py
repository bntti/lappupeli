from typing import Union
from uuid import uuid4
import urllib.parse
from markupsafe import Markup
from werkzeug.exceptions import NotFound
from flask import Response, abort, redirect, render_template, request, session
import random
from app import app
import database_service as dts

EMPTY = "Sait tyhjän lapun!"


# Functions
def check_uuid() -> None:
    if "uuid" not in session:
        session["uuid"] = uuid4()


def check_admin(room_id: int) -> bool:
    check_uuid()
    admin_uuid = dts.get_config(room_id)["admin_uuid"]
    return admin_uuid == session["uuid"]


def clear_confirm() -> None:
    session["confirm"] = None


def check_room(room_name: str) -> int:
    room_id = dts.get_room_id(room_name)
    if not room_id:
        abort(404, f"Ei huonetta nimellä {room_name}")
    return room_id


def next_word(room_id: int) -> None:
    words = dts.get_words(room_id)
    if len(words) == 0:
        return

    players = dts.get_config(room_id)["players"]
    dts.clear_player_words(room_id)

    r = random.randint(1, 10)
    tuple = dts.pop_word(room_id) if r != 1 else (EMPTY, None)
    next_word, suggester_uuid = tuple

    for _ in range(players - 2):
        dts.add_to_player_list(room_id, next_word)
    dts.add_to_player_list(room_id, EMPTY)
    dts.next_word(room_id, next_word, suggester_uuid)


def get_word(room_id: int) -> str:
    config = dts.get_config(room_id)

    if dts.has_word(room_id, session["uuid"]):
        return dts.get_word(room_id, session["uuid"])
    if session["uuid"] == config["suggester_uuid"]:
        dts.add_suggester_to_player_list(
            room_id, config["current_word"], config["suggester_uuid"]
        )
        return config["current_word"]
    if dts.get_player_list_size(room_id) == 0:
        return "Ei lappuja jäljellä"
    if dts.get_player_list_size(room_id) == dts.get_seen_count(room_id):
        return f"Lappuja on jo jaettu {config['players']} kpl"

    dts.give_word(room_id, session["uuid"])
    return dts.get_word(room_id, session["uuid"])


def clear_words(room_id: int) -> None:
    dts.clear_tables(room_id)


# 404 Error handler
@app.errorhandler(404)
def page_not_found(error: NotFound):
    return render_template('error.html', error=error.description), 404


# Url encoder
@app.template_filter('urlencode')
def url_encode(string: str) -> Markup:
    if isinstance(string, Markup):
        string = string.unescape()
    string = string.encode('utf8')
    string = urllib.parse.quote(string)
    return Markup(string)


# Routes
@app.route("/", methods=["GET"])
def index_get() -> str:
    clear_confirm()
    return render_template("index.html", rooms=dts.get_rooms())


@app.route("/", methods=["POST"])
def index_post() -> str:
    room_name = request.form.get("room_name")
    dts.add_room(room_name)
    return index_get()


@app.route("/room/<path:room_name>", methods=["GET"])
def room_get(room_name: str) -> str:
    check_uuid()
    room_id = check_room(room_name)
    new = (not dts.has_word(room_id, session["uuid"])
           and dts.get_player_list_size(room_id) > 0)
    return render_template(
        "room.html",
        words=dts.get_words(room_id),
        config=dts.get_config(room_id),
        seen_count=dts.get_seen_count(room_id),
        no_words=dts.get_player_list_size(room_id) == 0,
        new=new,
        room_name=room_name,
        admin=check_admin(room_id)
    )


@app.route("/room/<path:room_name>", methods=["POST"])
def room_post(room_name: str) -> Union[str, Response]:
    check_uuid()
    room_id = check_room(room_name)

    # User
    if request.form.get("word"):
        dts.add_word(room_id, request.form.get("word"), session["uuid"])
    if request.form.get("be_admin"):
        dts.set_admin_uuid(room_id, session["uuid"])

    # Admin
    if not check_admin(room_id):
        return room_get(room_name)

    if request.form.get("players"):
        dts.set_players(room_id, int(request.form.get("players")))
    if request.form.get("unbe_admin"):
        dts.set_admin_uuid(room_id, None)

    if request.form.get("cancel"):
        clear_confirm()
    if request.form.get("confirm"):
        if session["confirm"] == "confirm_delete_room":
            dts.delete_room(room_id)
            clear_confirm()
            return redirect("/")
        elif session["confirm"] == "confirm_clear":
            clear_words(room_id)
        elif session["confirm"] == "confirm_next_word":
            next_word(room_id)
        clear_confirm()
    if request.form.get("next_word"):
        if dts.get_player_list_size(room_id) != dts.get_seen_count(room_id):
            session["confirm"] = "confirm_next_word"
            session["confirm_message"] = "Kaikki eivät ole vielä valinneet sanaansa, haluatko varmasti seuraavan sanan?"
        else:
            next_word(room_id)
    if request.form.get("clear"):
        session["confirm"] = "confirm_clear"
        session["confirm_message"] = "Haluatko varmasti poistaa kaikki sanat?"
    if request.form.get("delete_room"):
        session["confirm"] = "confirm_delete_room"
        session["confirm_message"] = "Haluatko varmasti poistaa huoneen?"

    return room_get(room_name)


@app.route("/room/<path:room_name>/word")
def word(room_name: str) -> str:
    check_uuid()
    room_id = check_room(room_name)
    return render_template("word.html", room_name=room_name, word=get_word(room_id))
