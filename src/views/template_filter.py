import urllib.parse

from flask import Blueprint
from markupsafe import Markup

template_filter_bp = Blueprint("filter", __name__)


@template_filter_bp.app_template_filter("urlencode")
def url_encode(string: str) -> Markup:
    if isinstance(string, Markup):
        string = string.unescape()
    string = string.encode("utf8")
    string = urllib.parse.quote(string)
    return Markup(string)
