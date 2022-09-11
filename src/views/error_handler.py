from flask import Blueprint, render_template
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

error_handler_bp = Blueprint("error_handler", __name__)


@error_handler_bp.app_errorhandler(400)
def bad_request(error: BadRequest) -> tuple[str, int]:
    return render_template("error.html", error=error.description), 400


@error_handler_bp.app_errorhandler(401)
def unauthorized(_: Unauthorized) -> tuple[str, int]:
    return render_template("login.html"), 401


@error_handler_bp.app_errorhandler(404)
def page_not_found(error: NotFound) -> tuple[str, int]:
    return render_template("error.html", error=error.description), 404
