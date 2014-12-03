from datetime import datetime
from flask.json import JSONEncoder


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
