from flask import Flask

from config import SECRET_KEY, URL
from database import database
from views import error_handler, index, login, logout, room, template_filter


def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = 1024
    app.config["SQLALCHEMY_DATABASE_URI"] = URL

    database.init_app(app)

    app.register_blueprint(error_handler.error_handler_bp)
    app.register_blueprint(template_filter.template_filter_bp)
    app.register_blueprint(index.index_bp)
    app.register_blueprint(login.login_bp)
    app.register_blueprint(logout.logout_bp)
    app.register_blueprint(room.room_bp)

    return app
