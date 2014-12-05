from datetime import datetime
from flask.json import JSONEncoder
from flask import url_for, jsonify

time_format = '%Y-%m-%d %H:%M:%S'


class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime(time_format)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)



from TestSheriff_flask import app

app.json_encoder = CustomJSONEncoder

from . import status
app.register_blueprint(status.status_bp, url_prefix='/v1/statuses')

@app.route('/', methods=['GET'])
def index():
    links = {'self': {'href': url_for('index')},
             'statuses': {'href': url_for('status_v1.list')}
            }
    return jsonify(result='Success', _links=links)