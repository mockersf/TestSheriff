from flask import url_for
from werkzeug.routing import BuildError


def build_url_other(endpoint, **values):
    try:
        return url_for(endpoint, **values)
    except BuildError:
        pass
