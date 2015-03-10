import os, sys

import json
import pymongo
import datetime
import uuid
from bson.objectid import ObjectId
from random import randint
import bson
import random

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
        Base.BASE_PREFIX = 'test'
        from core.Status import Status
        self._base_status = Base.Base().get_base()[Status.collection]
        from core.Test import Test
        self._base_test = Base.Base().get_base()[Test.collection]
        app = Flask(__name__)
        app_api = restful.Api(app)
        import api.status
        api.status.add_status(app_api, root='/', version='test')
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

    def test_list_page_filter(self):
        from core.Status import Status
        from core import Base
        my_id1 = str(uuid.uuid4())
        my_id2 = str(uuid.uuid4())
        my_type1 = str(uuid.uuid4())
        my_type2 = str(uuid.uuid4())
        nb = random.randint(110, 150)
        datas = {}
        for i in range(nb):
            status = random.choice(['SUCCESS', 'FAILURE'])
            my_id = random.choice([my_id1, my_id2])
            my_type = random.choice([my_type1, my_type2])
            my_browser = random.choice(['Chrome', 'Firefox', 'IE'])
            data = {'test_id': my_id, 'status': status, 'type': my_type,
                    'details': {'browser': my_browser, 'environment': 'master', 'i': i, 'p': '{0}'.format(i % 2), 'random': str(uuid.uuid4())}}
            datas[i] = data
            json_query = prepare_json_query(data)
            rv = self.app_status.post('/test/statuses', headers=json_query['headers'], data=json_query['json'])
            assert rv.status_code == 200
            res = json.loads(rv.data.decode('utf-8'))
            Base.Base().upsert_by_id(Status.collection, bson.ObjectId(res['status']['_id']), {Status._on: datetime.datetime.now() - datetime.timedelta(seconds=nb - i + 1)})
            if i % 9 == 0:
                rv = self.app_status.get('/test/statuses')
                assert rv.status_code == 200
                res = json.loads(rv.data.decode('utf-8'))
                assert res['count'] == 100 if i + 1 > 100 else i + 1
                assert res['total'] == i + 1
                assert len(res['statuses']) == 100 if i + 1 > 100 else i + 1
        rv = self.app_status.get('/test/statuses')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['total'] == nb
        assert res['count'] == 100
        assert len(res['statuses']) == 100
        for i in range(100):
            assert res['statuses'][i]['details'] == datas[nb - i - 1]['details']
        rv = self.app_status.get('/test/statuses?page=1&nb_status=3')
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['count'] == 3
        assert len(res['statuses']) == 3
        assert res['statuses'][0]['details'] == datas[nb - 4]['details']
        assert res['statuses'][1]['details'] == datas[nb - 5]['details']
        assert res['statuses'][2]['details'] == datas[nb - 6]['details']
        rv = self.app_status.get('/test/statuses?test_id={0}'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['test_id'] == my_id1]
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['test_id'] == my_id1
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?test_id=!{0}'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['test_id'] != my_id1]
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['test_id'] != my_id1
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?type={0}'.format(my_type1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['type'] == my_type1]
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['type'] == my_type1
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?type=!{0}'.format(my_type1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['type'] != my_type1]
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['type'] != my_type1
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?status={0}'.format('SUCCESS'))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['status'] == 'SUCCESS']
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['status'] == 'SUCCESS'
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?status=!{0}'.format('SUCCESS'))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['status'] != 'SUCCESS']
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['status'] != 'SUCCESS'
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?field={0}&value={1}'.format('p', '0'))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['details']['p'] == '0']
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['details']['p'] == '0'
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        rv = self.app_status.get('/test/statuses?field={0}&value=!{1}'.format('p', '0'))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        datas_filtered = [datas[i] for i in datas if datas[i]['details']['p'] != '0']
        assert res['total'] == len(datas_filtered)
        assert res['count'] == len(datas_filtered)
        assert len(res['statuses']) == len(datas_filtered)
        for i in range(res['count']):
            assert res['statuses'][i]['details']['p'] != '0'
            assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i - 1]['details']
        next_page = '/test/statuses?field={0}&value={1}&page=0&nb_status=5'.format('p', '0')
        s_all_page_api = []
        i_all_page_api = 0
        datas_filtered = [datas[i] for i in datas if datas[i]['details']['p'] == '0']
        while next_page is not None:
            rv = self.app_status.get(next_page)
            assert rv.status_code == 200
            res = json.loads(rv.data.decode('utf-8'))
            for i in range(res['count']):
                assert res['statuses'][i]['details']['p'] == '0'
                assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i_all_page_api - 1]['details']
                s_all_page_api.append(res['statuses'][i])
                i_all_page_api += 1
            if 'next' in res['pagination']:
                next_page = res['pagination']['next']['href']
            else:
                next_page = None
        assert len(s_all_page_api) == len(datas_filtered)
        next_page = '/test/statuses?field1={0}&value1={1}&field2={2}&value2={3}&page=0&nb_status=7'.format('p', '0', 'browser', 'Chrome')
        s_all_page_api = []
        i_all_page_api = 0
        datas_filtered = [datas[i] for i in datas if datas[i]['details']['p'] == '0' and datas[i]['details']['browser'] == 'Chrome']
        while next_page is not None:
            rv = self.app_status.get(next_page)
            assert rv.status_code == 200
            res = json.loads(rv.data.decode('utf-8'))
            for i in range(res['count']):
                assert res['statuses'][i]['details']['p'] == '0'
                assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i_all_page_api - 1]['details']
                s_all_page_api.append(res['statuses'][i])
                i_all_page_api += 1
            if 'next' in res['pagination']:
                next_page = res['pagination']['next']['href']
            else:
                next_page = None
        assert len(s_all_page_api) == len(datas_filtered)
        next_page = '/test/statuses?field1={0}&value1={1}&field2={2}&value2=!{3}&page=0&nb_status=12'.format('p', '0', 'browser', 'Chrome')
        s_all_page_api = []
        i_all_page_api = 0
        datas_filtered = [datas[i] for i in datas if datas[i]['details']['p'] == '0' and datas[i]['details']['browser'] != 'Chrome']
        while next_page is not None:
            rv = self.app_status.get(next_page)
            assert rv.status_code == 200
            res = json.loads(rv.data.decode('utf-8'))
            for i in range(res['count']):
                assert res['statuses'][i]['details']['p'] == '0'
                assert res['statuses'][i]['details'] == datas_filtered[len(datas_filtered) - i_all_page_api - 1]['details']
                s_all_page_api.append(res['statuses'][i])
                i_all_page_api += 1
            if 'next' in res['pagination']:
                next_page = res['pagination']['next']['href']
            else:
                next_page = None
        assert len(s_all_page_api) == len(datas_filtered)



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
