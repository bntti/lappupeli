from typing import Union

from flask import Blueprint, abort, redirect, render_template, request, session
from werkzeug.wrappers.response import Response

login_bp = Blueprint("login", __name__)


@login_bp.route("/login", methods=["GET", "POST"])
def login() -> Union[str, Response]:
    if request.method == "POST" and request.form.get("username"):
        username = request.form["username"]
        if 0 < len(username) <= 32:
            session["username"] = username
            return redirect("/")
        abort(
            400,
            "Käyttäjänimi ei saa olla tyhjä ja sen pituus saa olla enintään 32 merkkiä",
        )
    return render_template("login.html")
