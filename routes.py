from typing import Union
import urllib.parse
from markupsafe import Markup
from werkzeug.exceptions import NotFound, Unauthorized, BadRequest
from flask import Response, abort, redirect, render_template, request, session, jsonify
from app import app
from repositories import card_repository, room_repository, word_repository, ready_player_repository
import game_service as game_service


# Error handlers
@app.errorhandler(400)
def page_not_found(error: BadRequest) -> tuple[str, int]:
    return render_template('error.html', error=error.description), 400


@app.errorhandler(401)
def unauthorized(_: Unauthorized) -> tuple[str, int]:
    return render_template('login.html'), 401


@app.errorhandler(404)
def page_not_found(error: NotFound) -> tuple[str, int]:
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
def index_get() -> Union[str, Response]:
    username = game_service.check_user()
    session["confirm"] = None
    ready_player_repository.set_player_to_not_ready(username)
    return render_template("index.html", rooms=room_repository.get_rooms())


@app.route("/", methods=["POST"])
def index_post() -> str:
    game_service.check_user()
    if request.form.get("room_name"):
        game_service.add_room(request.form.get("room_name"))
    return index_get()


@app.route("/room/<path:room_name>/room_data", methods=["GET"])
def room_data_get(room_name: str) -> Response:
    game_service.check_user()
    room_id = game_service.check_room(room_name)
    return jsonify({
        "round_in_progress": card_repository.get_card_count(room_id) > 0,
        "ready_player_count": ready_player_repository.get_ready_player_count(room_id),
        "seen_count": card_repository.get_seen_card_count(room_id),
        "card_count": card_repository.get_card_count(room_id),
        "word_count": word_repository.get_word_count(room_id),
        "config": room_repository.get_config(room_id)
    })


@app.route("/room/<path:room_name>", methods=["GET"])
def room_get(room_name: str) -> str:
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)
    return render_template(
        "room.html",
        in_game=card_repository.has_card(room_id, username),
        ready=ready_player_repository.is_ready(room_id, username),
        ready_player_count=ready_player_repository.get_ready_player_count(
            room_id),
        seen=card_repository.has_seen_card(room_id, username),
        seen_count=card_repository.get_seen_card_count(room_id),
        card_count=card_repository.get_card_count(room_id),
        word_count=word_repository.get_word_count(room_id),
        round_in_progress=card_repository.get_card_count(room_id) > 0,
        config=room_repository.get_config(room_id),
        room_name=room_name
    )


@app.route("/room/<path:room_name>", methods=["POST"])
def room_post(room_name: str) -> Union[str, Response]:
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)

    # User
    if request.form.get("word"):
        game_service.add_word(room_id, request.form.get("word"), username)
    if request.form.get("be_ready"):
        ready_player_repository.set_ready(room_id, username)
    if request.form.get("unbe_ready"):
        ready_player_repository.set_not_ready(room_id, username)
    if request.form.get("be_admin"):
        room_repository.set_admin(room_id, username)

    # Admin
    if username != room_repository.get_config(room_id)["admin_username"]:
        return room_get(room_name)

    if request.form.get("unbe_admin"):
        room_repository.set_admin(room_id, None)
    if request.form.get("start_round"):
        game_service.start_round(room_id)

    # Confirm and cancel
    if request.form.get("cancel"):
        session["confirm"] = None
    if request.form.get("confirm"):
        if session["confirm"] == "confirm_delete_room":
            room_repository.delete_room(room_id)
            session["confirm"] = None
            return redirect("/")
        elif session["confirm"] == "confirm_reset_room":
            game_service.reset_room(room_id)
        elif session["confirm"] == "confirm_end_round":
            game_service.end_round(room_id)
        session["confirm"] = None

    # Actions that (might) require confirmation
    if request.form.get("end_round"):
        if card_repository.get_seen_card_count(room_id) != card_repository.get_card_count(room_id):
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
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)
    return render_template("word.html", room_name=room_name, word=game_service.get_card(room_id, username))


@app.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    if request.method == "POST" and request.form.get("username"):
        username = request.form.get("username")
        if 0 < len(username) <= 32:
            session["username"] = username
            return redirect('/')
        else:
            abort(
                400, "Käyttäjänimi ei saa olla tyhjä ja sen pituus saa olla enintään 32 merkkiä"
            )
    return render_template("login.html")


@app.route("/logout")
def logout() -> Response:
    if "username" in session:
        ready_player_repository.set_player_to_not_ready(session["username"])
        del session["username"]
    return redirect("/login")
