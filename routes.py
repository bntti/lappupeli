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


def check_user() -> None:
    if "username" not in session:
        abort(401)


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
    return render_template("index.html", rooms=room_service.get_rooms())


@app.route("/", methods=["POST"])
def index_post() -> Union[str, Response]:
    check_user()
    room_name = request.form.get("room_name")
    room_service.add_room(room_name)
    return index_get()


@app.route("/room/<path:room_name>", methods=["GET"])
def room_get(room_name: str) -> Union[str, Response]:
    check_user()
    room_id = room_service.check_room(room_name)
    new = (not card_service.has_card(room_id, session["username"])
           and card_service.get_card_count(room_id) > 0)
    return render_template(
        "room.html",
        words=word_service.get_words(room_id),
        config=room_service.get_config(room_id),
        seen_count=card_service.get_seen_card_count(room_id),
        no_words=card_service.get_card_count(room_id) == 0,
        new=new,
        room_name=room_name
    )


@app.route("/room/<path:room_name>", methods=["POST"])
def room_post(room_name: str) -> Union[str, Response]:
    check_user()
    room_id = room_service.check_room(room_name)

    # User
    if request.form.get("word"):
        word_service.add_word(room_id, request.form.get(
            "word"), session["username"])
    if request.form.get("be_admin"):
        room_service.set_admin(room_id, session["username"])

    # Admin
    if session["username"] != room_service.get_config(room_id)["admin_username"]:
        return room_get(room_name)

    if request.form.get("player_count"):
        room_service.set_player_count(
            room_id, int(request.form.get("player_count")))
    if request.form.get("unbe_admin"):
        room_service.set_admin(room_id, None)

    if request.form.get("cancel"):
        session["confirm"] = None
    if request.form.get("confirm"):
        if session["confirm"] == "confirm_delete_room":
            room_service.delete_room(room_id)
            session["confirm"] = None
            return redirect("/")
        elif session["confirm"] == "confirm_clear":
            game_service.reset_game(room_id)
        elif session["confirm"] == "confirm_next_word":
            game_service.next_word(room_id)
        session["confirm"] = None
    if request.form.get("next_word"):
        if card_service.get_card_count(room_id) != card_service.get_seen_card_count(room_id):
            session["confirm"] = "confirm_next_word"
            session["confirm_message"] = "Kaikki eivät ole vielä nähneet sanaansa, haluatko varmasti seuraavan sanan?"
        else:
            game_service.next_word(room_id)
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
    room_id = room_service.check_room(room_name)
    return render_template("word.html", room_name=room_name, word=game_service.get_word(room_id))


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
