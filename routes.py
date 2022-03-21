from typing import Union
import urllib.parse
from markupsafe import Markup
from werkzeug.exceptions import NotFound, Unauthorized
from flask import Response, abort, redirect, render_template, request, session
import random
from app import app
import database_service as dts

EMPTY = "Sait tyhjän lapun!"


# Functions
def check_user() -> None:
    if "username" not in session:
        abort(401)


def check_room(room_name: str) -> int:
    room_id = dts.get_room_id(room_name)
    if not room_id:
        abort(404, f"Ei huonetta nimellä {room_name}")
    return room_id


def next_word(room_id: int) -> None:
    words = dts.get_words(room_id)
    if len(words) == 0:
        return

    player_count = dts.get_config(room_id)["player_count"]
    dts.clear_player_words(room_id)

    r = random.randint(1, 10)
    tuple = dts.pop_word(room_id) if r != 1 else (EMPTY, None)
    next_word, suggester_username = tuple

    for _ in range(player_count - 2):
        dts.add_to_player_list(room_id, next_word)
    if not suggester_username:
        dts.add_to_player_list(room_id, next_word)
    dts.add_to_player_list(room_id, EMPTY)
    dts.next_word(room_id, next_word, suggester_username)


def get_word(room_id: int) -> str:
    config = dts.get_config(room_id)

    if dts.has_word(room_id, session["username"]):
        return dts.get_word(room_id, session["username"])
    if session["username"] == config["suggester_username"]:
        dts.add_seen_to_player_list(
            room_id, config["current_word"], config["suggester_username"]
        )
        return config["current_word"]
    if dts.get_player_list_size(room_id) == 0:
        return "Peli ei ole vielä alkanut"
    if dts.get_player_list_size(room_id) == dts.get_seen_count(room_id):
        if dts.get_seen_count(room_id) != config['player_count']:
            # The suggester left the game (hopefully)
            dts.add_seen_to_player_list(
                room_id, config["current_word"], session["username"]
            )
            return config["current_word"]
        return f"Lappuja on jo jaettu {config['player_count']} kpl"

    dts.give_word(room_id, session["username"])
    return dts.get_word(room_id, session["username"])


# 404 Error handler
@app.errorhandler(404)
def page_not_found(error: NotFound) -> tuple[str, int]:
    return render_template('error.html', error=error.description), 404


# 401 Error handler
@app.errorhandler(401)
def unauthorized(_: Unauthorized) -> tuple[str, int]:
    return render_template('login.html'), 401


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
def index_get() -> Union[str, Response]:
    check_user()
    session["confirm"] = None
    return render_template("index.html", rooms=dts.get_rooms())


@app.route("/", methods=["POST"])
def index_post() -> Union[str, Response]:
    check_user()
    room_name = request.form.get("room_name")
    dts.add_room(room_name)
    return index_get()


@app.route("/room/<path:room_name>", methods=["GET"])
def room_get(room_name: str) -> Union[str, Response]:
    check_user()
    room_id = check_room(room_name)
    new = (not dts.has_word(room_id, session["username"])
           and dts.get_player_list_size(room_id) > 0)
    return render_template(
        "room.html",
        words=dts.get_words(room_id),
        config=dts.get_config(room_id),
        seen_count=dts.get_seen_count(room_id),
        no_words=dts.get_player_list_size(room_id) == 0,
        new=new,
        room_name=room_name
    )


@app.route("/room/<path:room_name>", methods=["POST"])
def room_post(room_name: str) -> Union[str, Response]:
    check_user()
    room_id = check_room(room_name)

    # User
    if request.form.get("word"):
        dts.add_word(room_id, request.form.get("word"), session["username"])
    if request.form.get("be_admin"):
        dts.set_admin(room_id, session["username"])

    # Admin
    if session["username"] != dts.get_config(room_id)["admin_username"]:
        return room_get(room_name)

    if request.form.get("player_count"):
        dts.set_player_count(room_id, int(request.form.get("player_count")))
    if request.form.get("unbe_admin"):
        dts.set_admin(room_id, None)

    if request.form.get("cancel"):
        session["confirm"] = None
    if request.form.get("confirm"):
        if session["confirm"] == "confirm_delete_room":
            dts.delete_room(room_id)
            session["confirm"] = None
            return redirect("/")
        elif session["confirm"] == "confirm_clear":
            dts.reset_room(room_id)
        elif session["confirm"] == "confirm_next_word":
            next_word(room_id)
        session["confirm"] = None
    if request.form.get("next_word"):
        if dts.get_player_list_size(room_id) != dts.get_seen_count(room_id):
            session["confirm"] = "confirm_next_word"
            session["confirm_message"] = "Kaikki eivät ole vielä nähneet sanaansa, haluatko varmasti seuraavan sanan?"
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
def word(room_name: str) -> Union[str, Response]:
    check_user()
    room_id = check_room(room_name)
    return render_template("word.html", room_name=room_name, word=get_word(room_id))


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    if request.method == "POST":
        if request.form.get("username"):
            username = request.form.get("username")
            if 0 < len(username) <= 64:
                session["username"] = username
                return redirect('/')
    return render_template("login.html")


@app.route("/logout")
def logout() -> Response:
    if "username" in session:
        del session["username"]
    return redirect("/login")
