from flask import Blueprint, redirect, session
from repositories import player_repository
from werkzeug.wrappers.response import Response

logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout")
def logout() -> Response:
    if "username" in session:
        player_repository.leave_rooms(session["username"])
        del session["username"]
    return redirect("/login")
