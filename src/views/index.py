from flask import Blueprint, render_template, request, session

import game_service
from repositories import player_repository, room_repository

index_bp = Blueprint("index", __name__)


@index_bp.route("/", methods=["GET"])
def index_get() -> str:
    username = game_service.check_user()
    session["confirm"] = None
    player_repository.leave_rooms(username)
    return render_template("index.html", rooms=room_repository.get_rooms())


@index_bp.route("/", methods=["POST"])
def index_post() -> str:
    game_service.check_user()
    if request.form.get("room_name"):
        game_service.add_room(request.form["room_name"])
    return index_get()
