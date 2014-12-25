import os, sys

import json
import pymongo
import datetime
import uuid
from bson.objectid import ObjectId
from random import randint

from flask import Flask, url_for
from flask.ext import restful

from tests import tools


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


def prepare_json_query(data):
    headers = [('Content-Type', 'application/json')]
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers.append(('Content-Length', json_data_length))
    return {'headers': headers, 'json': json_data}


class Test_api_testType(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'
        from core.Status import Status
        self._base_status = Base.Base().get_base()[Status.collection]
        from core.Test import Test
        self._base_test = Base.Base().get_base()[Test.collection]
        from core.TestType import TestType
        self._base_test_type = Base.Base().get_base()[TestType.collection]
        app = Flask(__name__)
        app_api = restful.Api(app)
        import api.testType
        api.testType.add_test_type(app_api, version='test')
        self.app_test_type = app.test_client()

    def teardown_method(self, method):
        tools.db_drop()

    def test_get_collection(self):
        from core.TestType import TestType
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type1 = TestType(my_type1, doc1)
        test_type1.save()
        my_type2 = str(uuid.uuid4())
        doc2 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type2 = TestType(my_type2, doc2)
        test_type2.save()
        rv = self.app_test_type.get('/test/test_types')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['count'] == 2
        assert [tt['type'] for tt in res['test_types']] == [my_type1, my_type2]

    def test_get(self):
        from core.TestType import TestType
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type1 = TestType(my_type1, doc1)
        test_type1.save()
        my_type2 = str(uuid.uuid4())
        doc2 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type2 = TestType(my_type2, doc2)
        test_type2.save()
        rv = self.app_test_type.get('/test/test_types/{0}'.format(my_type1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['test_type']['type'] == my_type1
        rv = self.app_test_type.get('/test/test_types/{0}'.format(str(uuid.uuid4())))
        assert rv.status_code == 404

    def test_indexes(self):
        from core.Index import Index
        from core.Status import Status
        from core.TestType import TestType
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = 'SUCCESS'
        test_type = str(uuid.uuid4())
        field1 = 'browser'
        field2 = 'environment'
        TestType(test_type, doc_fields_to_index=[field1, field2]).save()
        details1 = {field1: 'Firefox', field2: 'master'}
        status1 = Status(test_id, test_type, test_status, details=details1)
        status1.save()
        details2 = {field1: 'Chrome', field2: 'master'}
        status2 = Status(test_id, test_type, test_status, details=details2)
        status2.save()
        rv = self.app_test_type.get('/test/test_types/{0}/indexes'.format(test_type))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['count'] == 2
        assert sorted([index['field'] for index in res['indexes']]) == sorted(['browser', 'environment'])
        rv = self.app_test_type.get('/test/test_types/{0}/indexes'.format(str(uuid.uuid4())))
        assert rv.status_code == 404

    def test_index(self):
        from core.Index import Index
        from core.Status import Status
        from core.TestType import TestType
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = 'SUCCESS'
        test_type = str(uuid.uuid4())
        field1 = 'browser'
        field2 = 'environment'
        TestType(test_type, doc_fields_to_index=[field1, field2]).save()
        details1 = {field1: 'Firefox', field2: 'master'}
        status1 = Status(test_id, test_type, test_status, details=details1)
        status1.save()
        details2 = {field1: 'Chrome', field2: 'master'}
        status2 = Status(test_id, test_type, test_status, details=details2)
        status2.save()
        rv = self.app_test_type.get('/test/test_types/{0}/indexes/{1}'.format(str(uuid.uuid4()), field1))
        assert rv.status_code == 404
        rv = self.app_test_type.get('/test/test_types/{0}/indexes/{1}'.format(test_type, str(uuid.uuid4())))
        assert rv.status_code == 404
        rv = self.app_test_type.get('/test/test_types/{0}/indexes/{1}'.format(test_type, field1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['index']['field'] == field1
        assert res['index']['type'] == test_type
        assert sorted(res['index']['values']) == sorted(['Firefox', 'Chrome'])

    def test_patch_testtype(self):
        from core.TestType import TestType
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type1 = TestType(my_type1, doc1)
        test_type1.save()
        my_type2 = str(uuid.uuid4())
        doc2 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type2 = TestType(my_type2, doc2)
        test_type2.save()
        my_id1 = str(uuid.uuid4())
        data1 = {'doc_fields_to_index': [str(uuid.uuid4()), str(uuid.uuid4())]}
        json_query = prepare_json_query(data1)
        rv = self.app_test_type.patch('/test/test_types/{0}'.format(my_type1), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['test_type']['type'] == my_type1
        assert res['test_type']['doc_fields_to_index'] == data1['doc_fields_to_index']
        rv = self.app_test_type.patch('/test/test_types/{0}'.format(str(uuid.uuid4())), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 404

    def test_get_run(self):
        from core.Status import Status
        from core.TestType import TestType
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = 'SUCCESS'
        test_type = str(uuid.uuid4())
        field1 = 'browser'
        field2 = 'environment'
        tt = TestType(test_type, doc_fields_to_index=[field1, field2])
        tt.add_run_type('new', 'ANY', {'operator': 'EQUAL', 'field': 1, 'value': 1})
        tt.save()
        details1 = {field1: 'Firefox', field2: 'master'}
        status1 = Status(test_id, test_type, test_status, details=details1)
        status1.save()
        rv = self.app_test_type.get('/test/test_types/{0}/runs/{1}'.format(str(uuid.uuid4()), 'default'))
        assert rv.status_code == 404
        rv = self.app_test_type.get('/test/test_types/{0}/runs/{1}'.format(test_type, str(uuid.uuid4())))
        assert rv.status_code == 404
        rv = self.app_test_type.get('/test/test_types/{0}/runs/{1}'.format(test_type, 'default'))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run']['modifier'] == TestType._default_run['modifier']
        assert res['run']['condition'] == TestType._default_run['condition'].to_dict()
        rv = self.app_test_type.get('/test/test_types/{0}/runs/{1}'.format(test_type, 'new'))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['run']['modifier'] == 'ANY'
        assert res['run']['condition'] == {'operator': 'EQUAL', 'field': 1, 'value': 1}
        rv = self.app_test_type.get('/test/test_types/{0}/runs'.format(str(uuid.uuid4())))
        assert rv.status_code == 404
        rv = self.app_test_type.get('/test/test_types/{0}/runs'.format(test_type))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['count'] == 2
        rv = self.app_test_type.get('/test/test_types/{0}'.format(test_type))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert 'run' not in res['test_type']

    def test_post_run(self):
        from core.Status import Status
        from core.TestType import TestType
        from core.Base import Base
        test_type = str(uuid.uuid4())
#        field1 = 'browser'
#        field2 = 'environment'
        tt = TestType(test_type)#, doc_fields_to_index=[field1, field2])
        tt.save()
        my_run = str(uuid.uuid4())
        data = {'run_type': my_run, 'modifier': 'ANY', 'condition': {'operator': 'EQUAL', 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(str(uuid.uuid4())), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 404
        data = {'run_type': my_run, 'modifier': str(uuid.uuid4()), 'condition': {'operator': 'EQUAL', 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(test_type), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 400
        data = {'run_type': my_run, 'modifier': 'ANY', 'condition': {'operator': str(uuid.uuid4()), 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(test_type), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 400
        data = {'run_type': my_run, 'modifier': 'ANY', 'condition': {'operator': 'OR', 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(test_type), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 400
        data = {'run_type': my_run, 'modifier': 'ANY', 'condition': {'operator': 'OR', 'part1': str(uuid.uuid4()), 'part2': {'operator': 'EQUAL', 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(test_type), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 400
        data = {'run_type': my_run, 'modifier': 'ANY', 'condition': {'operator': 'OR', 'part1': {'operator': 'EQUAL', 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}, 'part2': str(uuid.uuid4())}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(test_type), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 400
        data = {'run_type': my_run, 'modifier': 'ALL', 'condition': {'operator': 'EQUAL', 'field': str(uuid.uuid4()), 'value': str(uuid.uuid4())}}
        json_query = prepare_json_query(data)
        rv = self.app_test_type.post('/test/test_types/{0}/runs'.format(test_type), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
