from typing import Union
import urllib.parse
from markupsafe import Markup
from werkzeug.exceptions import NotFound, Unauthorized
from flask import Response, abort, redirect, render_template, request, session
from app import app
import services.card_service as card_service
import services.room_service as room_service
import services.word_service as word_service
import services.game_service as game_service
import services.ready_players_service as rps


def check_user() -> str:
    if "username" not in session:
        abort(401)
    return session["username"]


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
    username = check_user()
    session["confirm"] = None
    rps.set_player_to_not_ready(username)
    return render_template("index.html", rooms=room_service.get_rooms())


@app.route("/", methods=["POST"])
def index_post() -> str:
    check_user()
    room_name = request.form.get("room_name")
    room_service.add_room(room_name)
    return index_get()


@app.route("/room/<path:room_name>", methods=["GET"])
def room_get(room_name: str) -> str:
    username = check_user()
    room_id = room_service.check_room(room_name)
    print(card_service.get_card_count(room_id))
    return render_template(
        "room.html",
        in_game=card_service.has_card(room_id, username),
        ready=rps.is_ready(room_id, username),
        ready_player_count=rps.get_ready_player_count(room_id),
        seen=card_service.has_seen_card(room_id, username),
        seen_count=card_service.get_seen_card_count(room_id),
        round_in_progress=card_service.get_card_count(room_id) > 0,
        word_count=word_service.get_word_count(room_id),
        config=room_service.get_config(room_id),
        room_name=room_name
    )


@app.route("/room/<path:room_name>", methods=["POST"])
def room_post(room_name: str) -> Union[str, Response]:
    username = check_user()
    room_id = room_service.check_room(room_name)

    # User
    if request.form.get("word"):
        word_service.add_word(room_id, request.form.get("word"), username)
    if request.form.get("be_ready"):
        rps.set_ready(room_id, username)
    if request.form.get("unbe_ready"):
        rps.set_not_ready(room_id, username)
    if request.form.get("be_admin"):
        room_service.set_admin(room_id, username)

    # Admin
    if username != room_service.get_config(room_id)["admin_username"]:
        return room_get(room_name)

    if request.form.get("unbe_admin"):
        room_service.set_admin(room_id, None)

    if request.form.get("cancel"):
        session["confirm"] = None
    if request.form.get("confirm"):
        if session["confirm"] == "confirm_delete_room":
            room_service.delete_room(room_id)
            session["confirm"] = None
            return redirect("/")
        elif session["confirm"] == "confirm_reset_room":
            game_service.reset_room(room_id)
        elif session["confirm"] == "confirm_end_round":
            game_service.end_round(room_id)
        session["confirm"] = None

    if request.form.get("start_round"):
        game_service.start_round(room_id)
    if request.form.get("end_round"):
        if card_service.get_seen_card_count(room_id) != card_service.get_card_count(room_id):
            session["confirm"] = "confirm_end_round"
            session["confirm_message"] = "Kaikki eivät ole vielä nähneet lappuansa, haluatko varmasti lopettaa kierroksen?"
        else:
            game_service.end_round(room_id)
    if request.form.get("reset_room"):
        session["confirm"] = "confirm_reset_room"
        session["confirm_message"] = "Haluatko varmasti nollata huoneen?"
    if request.form.get("delete_room"):
        session["confirm"] = "confirm_delete_room"
        session["confirm_message"] = "Haluatko varmasti poistaa huoneen?"

    return room_get(room_name)


@app.route("/room/<path:room_name>/word")
def word(room_name: str) -> str:
    username = check_user()
    room_id = room_service.check_room(room_name)
    return render_template("word.html", room_name=room_name, word=card_service.get_card(room_id, username))


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
        rps.set_player_to_not_ready(session["username"])
        del session["username"]
    return redirect("/login")
