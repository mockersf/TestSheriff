from datetime import datetime
from flask.json import JSONEncoder
from flask import url_for, jsonify
from flask.ext import restful


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
api = restful.Api(app)


from . import status
status.add_status(api)
from . import test
test.add_test(api)


@app.route('/', methods=['GET'])
def index():
    links = {'self': {'href': url_for('index')},
             'statuses': {'href': api.url_for(status.List)}
            }
    return jsonify(result='Success', _links=links)
