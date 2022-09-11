from flask import Blueprint, Response, redirect, session

from repositories import player_repository

logout_bp = Blueprint("logout", __name__)


@logout_bp.route("/logout")
def logout() -> Response:
    if "username" in session:
        player_repository.leave_rooms(session["username"])
        del session["username"]
    return redirect("/login")
