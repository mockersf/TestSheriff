import json
import datetime
import uuid

from flask import Flask, jsonify, request
from flask.json import JSONEncoder


def prepare_json_query(data):
    headers = [('Content-Type', 'application/json')]
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers.append(('Content-Length', json_data_length))
    return {'headers': headers, 'json': json_data}


class Test_api(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'
        from api import api
        my_app = api.app
        self.app = my_app.test_client()

    def teardown_method(self, method):
        from core import Base
        from core.Index import Index
        from core.Test import Test
        from core.Status import Status
        from core.TestType import TestType
        Base.Base().get_base()[Index.collection].drop()
        Base.Base().get_base()[Test.collection].drop()
        Base.Base().get_base()[Status.collection].drop()
        Base.Base().get_base()[TestType.collection].drop()

    def test_index(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.post('/v1/statuses', headers=json_query['headers'], data=json_query['json'])
        res_success = json.loads(rv.data.decode('utf-8'))
        data1 = {'test_id': my_id1, 'status': 'FAILURE', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.post('/v1/statuses', headers=json_query['headers'], data=json_query['json'])
        res_failure = json.loads(rv.data.decode('utf-8'))
        rv = self.app.get('/v1/tests/{0}'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['test']['_links']['last_status'] == res_failure['status']['_links']['self']
        assert res['test']['_links']['last_status_success'] == res_success['status']['_links']['self']
        assert res['test']['_links']['last_status_failure'] == res_failure['status']['_links']['self']

    def test_expand(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.post('/v1/statuses', headers=json_query['headers'], data=json_query['json'])
        res_success = json.loads(rv.data.decode('utf-8'))
        data1 = {'test_id': my_id1, 'status': 'FAILURE', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.post('/v1/statuses', headers=json_query['headers'], data=json_query['json'])
        res_failure = json.loads(rv.data.decode('utf-8'))
        rv = self.app.get('/v1/tests/{0}?expand=last_status,last_status_success'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert type(res['test']['last_status']) == type({})
        assert type(res['test']['last_status_success']) == type({})
        assert type(res['test']['last_status_failure']) in [type('String'), type(u'Unicode')]

    def test_expand_failed(self):
        from core import Base
        from core.Status import Status
        test_id = str(uuid.uuid4())
        test_status = 'SUCCESS'
        test_type = str(uuid.uuid4())
        status = Status(test_id, test_type, test_status)
        status_id = str(Base.Base().insert(Status.collection, status.to_dict()))
        rv = self.app.get('/v1/statuses/{0}'.format(status_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert type(res['status']['test']) in [type('String'), type(u'Unicode')]
        rv = self.app.get('/v1/statuses/{0}?expand=test'.format(status_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert type(res['status']['test']) in [type('String'), type(u'Unicode')]
