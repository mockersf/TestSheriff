import os, sys

import json
import pymongo
import datetime
import uuid
from bson.objectid import ObjectId
from random import randint

from flask import Flask, url_for
from flask.ext import restful


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def prepare_json_query(data):
    headers = [('Content-Type', 'application/json')]
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers.append(('Content-Length', json_data_length))
    return {'headers': headers, 'json': json_data}


class Test_api_test(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'
        from core.Status import Status
        self._base_status = Base.Base().get_base()[Status.collection]
        from core.Test import Test
        self._base_test = Base.Base().get_base()[Test.collection]
        app = Flask(__name__)
        app_api = restful.Api(app)
        import api.test
        api.test.add_test(app_api, version='test')
        self.app_test = app.test_client()

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

    def test_post_collection(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_test.post('/test/tests', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res1 = json.loads(rv.data.decode('utf-8'))
        assert res1['result'] == 'Success'
        assert res1['test']['test_id'] == my_id1
        rv = self.app_test.get(res1['test']['_links']['self']['href'])
        assert rv.status_code == 200
        res2 = json.loads(rv.data.decode('utf-8'))
        assert res2 == res1

    def test_get(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_test.post('/test/tests', headers=json_query['headers'], data=json_query['json'])
        res1 = json.loads(rv.data.decode('utf-8'))
        rv = self.app_test.get('/test/tests/{0}'.format(uuid.uuid4()))
        assert rv.status_code == 404
        rv = self.app_test.get('/test/tests/{0}'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res1['test']['test_id'] == my_id1

    def test_list(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_test.post('/test/tests', headers=json_query['headers'], data=json_query['json'])
        res1 = json.loads(rv.data.decode('utf-8'))
        rv = self.app_test.get('/test/tests')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert len(res['tests']) == 1
        assert res['tests'][0]['test_id'] == my_id1
        rv = self.app_test.get('/test/tests?test_type=test_tool')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert len(res['tests']) == 1
        rv = self.app_test.get('/test/tests?test_type=zut')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert len(res['tests']) == 0

    def test_should_i_run_default(self):
        from core.Status import Status
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        details = {'browser': 'Firefox'}
        test_type = str(uuid.uuid4())
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        rv = self.app_test.get('/test/tests/{0}/run'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == False
        test_id2 = str(uuid.uuid4())
        test_status2 = 'SUCCESS'
        status2 = Status(test_id2, test_type, test_status2, details=details)
        status2.save_and_update()
        rv = self.app_test.get('/test/tests/{0}/run'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == False
        test_status3 = 'SUCCESS'
        test_type = str(uuid.uuid4())
        status3 = Status(test_id, test_type, test_status3, details=details)
        status3.save_and_update()
        rv = self.app_test.get('/test/tests/{0}/run'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == True
        rv = self.app_test.get('/test/tests/{0}/run'.format(str(uuid.uuid4())))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == True
        rv = self.app_test.get('/test/tests/{0}/run/default'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == True

    def test_should_i_run_custom(self):
        from core.Status import Status
        from core.TestType import TestType
        test_type = str(uuid.uuid4())
        tt = TestType(test_type)
        tt._run = {'ALLOK':
                    {
                        'condition': {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'SUCCESS'},
                        'modifier': 'ALL'
                    }
                  }
        tt.save()
        test_id = str(uuid.uuid4())
        details = {'browser': 'Firefox'}
        test_type = str(uuid.uuid4())
        test_status1 = 'SUCCESS'
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        rv = self.app_test.get('/test/tests/{0}/run/ALLOK'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == True
        test_status2 = 'FAILURE'
        status2 = Status(test_id, test_type, test_status2, details=details)
        status2.save_and_update()
        rv = self.app_test.get('/test/tests/{0}/run/ALLOK'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == False
        rv = self.app_test.get('/test/tests/{0}/run'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == False
        test_status2 = 'SUCCESS'
        status2 = Status(test_id, test_type, test_status2, details=details)
        status2.save_and_update()
        rv = self.app_test.get('/test/tests/{0}/run/ALLOK'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == False
        rv = self.app_test.get('/test/tests/{0}/run'.format(test_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run'] == True
        rv = self.app_test.get('/test/tests/{0}/run/{1}'.format(test_id, str(uuid.uuid4())))
        assert rv.status_code == 404
