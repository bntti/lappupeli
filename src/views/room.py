from typing import Union

from flask import (
    Blueprint,
    Response,
    jsonify,
    redirect,
    render_template,
    request,
    session,
)

import game_service
from repositories import (
    card_repository,
    player_repository,
    room_repository,
    word_repository,
)

room_bp = Blueprint("room", __name__)


@room_bp.route("/room/<path:room_name>/room_data", methods=["GET"])
def room_data_get(room_name: str) -> Response:
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)
    players = player_repository.get_players(room_id)
    return jsonify(
        {
            "in_room": username in players,
            "round_in_progress": game_service.round_in_progress(room_id),
            "seen_count": card_repository.get_seen_card_count(room_id),
            "player_count": player_repository.get_player_count(room_id),
            "word_count": word_repository.get_word_count(room_id),
            "players": players,
            "config": room_repository.get_config(room_id),
        }
    )


@room_bp.route("/room/<path:room_name>", methods=["GET"])
def room_get(room_name: str) -> str:
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)
    round_in_progress = game_service.round_in_progress(room_id)
    if not round_in_progress:
        player_repository.join_room(room_id, username)
    return render_template(
        "room.html",
        in_game=card_repository.has_card(room_id, username),
        round_in_progress=round_in_progress,
        seen=card_repository.has_seen_card(room_id, username),
        seen_count=card_repository.get_seen_card_count(room_id),
        player_count=player_repository.get_player_count(room_id),
        word_count=word_repository.get_word_count(room_id),
        config=room_repository.get_config(room_id),
        players=player_repository.get_players(room_id),
        room_name=room_name,
    )


@room_bp.route("/room/<path:room_name>", methods=["POST"])
def room_post(room_name: str) -> Union[str, Response]:
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)

    # User
    if request.form.get("word"):
        game_service.add_word(room_id, request.form.get("word"), username)
    if request.form.get("be_admin"):
        room_repository.set_admin(room_id, username)

    # Admin
    if username != room_repository.get_config(room_id)["admin_username"]:
        return room_get(room_name)

    if request.form.get("unbe_admin"):
        room_repository.set_admin(room_id, None)
    if request.form.get("start_round"):
        game_service.start_round(room_id)
    for player in player_repository.get_players(room_id):
        if request.form.get(f"remove_player_{player}"):
            player_repository.leave_rooms(player)

    # Confirm and cancel
    if request.form.get("cancel"):
        session["confirm"] = None
    if request.form.get("confirm"):
        if session["confirm"] == "confirm_delete_room":
            room_repository.delete_room(room_id)
            session["confirm"] = None
            return redirect("/")
        if session["confirm"] == "confirm_reset_room":
            game_service.reset_room(room_id)
        elif session["confirm"] == "confirm_end_round":
            game_service.end_round(room_id)
        session["confirm"] = None

    # Actions that (might) require confirmation
    if request.form.get("end_round"):
        if card_repository.get_seen_card_count(
            room_id
        ) != card_repository.get_card_count(room_id):
            session["confirm"] = "confirm_end_round"
            session[
                "confirm_message"
            ] = "Kaikki eivät ole vielä nähneet lappuansa, haluatko varmasti lopettaa kierroksen?"
        else:
            game_service.end_round(room_id)
    if request.form.get("reset_room"):
        session["confirm"] = "confirm_reset_room"
        session["confirm_message"] = "Haluatko varmasti nollata huoneen?"
    if request.form.get("delete_room"):
        session["confirm"] = "confirm_delete_room"
        session["confirm_message"] = "Haluatko varmasti poistaa huoneen?"

    return room_get(room_name)


@room_bp.route("/room/<path:room_name>/word")
def word(room_name: str) -> str:
    username = game_service.check_user()
    room_id = game_service.check_room(room_name)
    return render_template(
        "word.html", room_name=room_name, word=game_service.get_card(room_id, username)
    )
