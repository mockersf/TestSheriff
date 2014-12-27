import json
import datetime

from flask import Flask, jsonify, request
from flask.json import JSONEncoder


class Test_api(object):
    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_flask_app(self):
        from api import api
        my_app = api.app
        assert my_app.name == 'TestSheriff_flask'
        now = datetime.datetime.now()
        @my_app.route('/test_json_datetime')
        def json_datetime():
            return jsonify(result=now)
        rv = my_app.test_client().get('/test_json_datetime')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res == {'result': now.strftime(api.time_format)}

    def test_jsonencoder(self):
        from api import api
        app = Flask(__name__)
        app.json_encoder = api.CustomJSONEncoder
        @app.route('/test_json_basic')
        def json_basic():
            return jsonify(result='test')
        now = datetime.datetime.now()
        @app.route('/test_json_datetime')
        def json_datetime():
            return jsonify(result=now)
        @app.route('/test_json_iter')
        def json_iter():
            class Counter:
                def __init__(self, value):
                    self._value = value
                    self._current = 0
                def __iter__(self):
                    return self
                def __next__(self):
                    if self._current > self._value:
                        raise StopIteration
                    else:
                        self._current += 1
                        return self._current - 1
                def next(self):
                    return self.__next__()
            return jsonify(result=Counter(5))
        @app.route('/test_json_error')
        def json_error():
            class NewObject:
                def __init__(self, value):
                    self._value = value
            return jsonify(result=NewObject(5))
        test_app = app.test_client()
        rv = test_app.get('/test_json_basic')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res == {'result': 'test'}
        rv = test_app.get('/test_json_datetime')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res == {'result': now.strftime(api.time_format)}
        rv = test_app.get('/test_json_iter')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res == {'result': [0, 1, 2, 3, 4, 5]}
        rv = test_app.get('/test_json_error')
        assert rv.status_code == 500

    def test_index(self):
        from api import api
        my_app = api.app
        rv = my_app.test_client().get('/api')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['_links'] == {'self': {'href': '/api'},
                                 'statuses': {'href': '/api/v1/statuses'},
                                 'tests': {'href': '/api/v1/tests'},
                                 'test types': {'href': '/api/v1/test_types'},
                                }
