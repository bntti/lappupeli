from typing import Union

import game_service as game_service
from flask import Blueprint, Response, render_template, request, session
from repositories import player_repository, room_repository

index_bp = Blueprint("index", __name__)


@index_bp.route("/", methods=["GET"])
def index_get() -> Union[str, Response]:
    username = game_service.check_user()
    session["confirm"] = None
    player_repository.leave_rooms(username)
    return render_template("index.html", rooms=room_repository.get_rooms())


@index_bp.route("/", methods=["POST"])
def index_post() -> str:
    game_service.check_user()
    if request.form.get("room_name"):
        game_service.add_room(request.form.get("room_name"))
    return index_get()
