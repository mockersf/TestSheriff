import os, sys

import json
import pymongo
import datetime
import uuid
from bson.objectid import ObjectId
from random import randint
import bson

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


class Test_api_status(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'
        from core.Status import Status
        self._base_status = Base.Base().get_base()[Status.collection]
        from core.Test import Test
        self._base_test = Base.Base().get_base()[Test.collection]
        app = Flask(__name__)
        app_api = restful.Api(app)
        import api.status
        api.status.add_status(app_api, version='test')
        self.app_status = app.test_client()

    def teardown_method(self, method):
        tools.db_drop()

    def test_post_collection(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res1 = json.loads(rv.data.decode('utf-8'))
        assert res1['result'] == 'Success'
        assert res1['status']['details'] == data1['details']
        rv = self.app_status.get(res1['status']['_links']['self']['href'])
        assert rv.status_code == 200
        res2 = json.loads(rv.data.decode('utf-8'))
        assert res2['status'] == res1['status']

    def test_get(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        res1 = json.loads(rv.data.decode('utf-8'))
        rv = self.app_status.get('/test/statuses/{0}'.format(uuid.uuid4()))
        assert rv.status_code == 404
        rv = self.app_status.get('/test/statuses/{0}'.format(res1['status']['_id']))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['status']['details'] == data1['details']
        assert res['status']['status'] == 'SUCCESS'
        assert res['status']['_links']['self'] == {'href': '/test/statuses/{0}'.format(res1['status']['_id'])}

    def test_delete(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        res1 = json.loads(rv.data.decode('utf-8'))
        rv = self.app_status.delete('/test/statuses/{0}'.format(res1['status']['_id']))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        rv = self.app_status.get('/test/statuses/{0}'.format(res1['status']['_id']))
        assert rv.status_code == 404

    def test_list(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res1 = json.loads(rv.data.decode('utf-8'))
        rv = self.app_status.get('/test/statuses')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['count'] == 1
        assert len(res['statuses']) == 1
        assert res['statuses'][0]['details'] == data1['details']
        assert res['statuses'][0]['_links']['self'] == {'href': '/test/statuses/{0}'.format(res1['status']['_id'])}
        data2 = {'test_id': my_id1, 'status': 'FAILURES', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data2)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        my_id2 = str(uuid.uuid4())
        data3 = {'test_id': my_id2, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data3)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        rv = self.app_status.get('/test/statuses')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['count'] == 3
        rv = self.app_status.get('/test/statuses?test_id={0}'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['count'] == 2

    def test_post_collection_purge(self):
        from core.Status import Status
        from core.Base import Base
        my_id1 = str(uuid.uuid4())
        data1 = {'test_id': my_id1, 'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res1 = json.loads(rv.data.decode('utf-8'))
        assert res1['result'] == 'Success'
        assert res1['status']['details'] == data1['details']
        assert res1['purge'] == {'nb_removed': 0}
        rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res2 = json.loads(rv.data.decode('utf-8'))
        assert res2['result'] == 'Success'
        assert res2['purge'] == {'nb_removed': 0}
        Base().upsert_by_id(Status.collection, bson.ObjectId(res1['status']['_id']), {Status._on: datetime.datetime.now() - datetime.timedelta(days=8)})
        rv = self.app_status.post('/test/statuses?purge=zut', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 400
        rv = self.app_status.post('/test/statuses?purge=false', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res2 = json.loads(rv.data.decode('utf-8'))
        assert res2['result'] == 'Success'
        assert res2['purge'] == None
        rv = self.app_status.post('/test/statuses?purge=True', headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        res2 = json.loads(rv.data.decode('utf-8'))
        assert res2['result'] == 'Success'
        assert res2['purge'] == {'nb_removed': 1}
