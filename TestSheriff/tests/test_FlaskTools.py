import json
import datetime

from flask import Flask, jsonify, request
from flask.json import JSONEncoder


class Test_TestSheriff(object):
    def setup_method(self, method):
        pass

    def teardown_method(self, method):
        pass

    def test_jsonencoder(self):
        import TestSheriff
        app = Flask('test_app')
        app.json_encoder = TestSheriff.CustomJSONEncoder
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
                def next(self):
                    if self._current > self._value:
                        raise StopIteration
                    else:
                        self._current += 1
                        return self._current - 1
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
        assert res == {'result': now.strftime(TestSheriff.time_format)}
        rv = test_app.get('/test_json_iter')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res == {'result': [0, 1, 2, 3, 4, 5]}
        rv = test_app.get('/test_json_error')
        assert rv.status_code == 500

