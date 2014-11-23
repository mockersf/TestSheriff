import json
import pymongo
import datetime
import uuid
from bson.objectid import ObjectId
from random import randint


base_prefix = ""
def base():
    connection = pymongo.MongoClient('localhost', 27017)
    base_status = connection[base_prefix + 'TestSheriff']#['status']
    return base_status

def prepare_json_query(data):
    headers = [('Content-Type', 'application/json')]
    json_data = json.dumps(data)
    json_data_length = len(json_data)
    headers.append(('Content-Length', json_data_length))
    return {'headers': headers, 'json': json_data}

class Test_TestSheriff(object):
    def setup_method(self, method):
        import TestSheriff
        from core import Base
        self.app = TestSheriff.app.test_client()
        self._base_status = base()['status']
        self._base_test = base()['test']

    def teardown_method(self, method):
        self._base_status.drop()
        self._base_test.drop()

    def test_save_1_status(self):
        my_id = str(uuid.uuid4())
        data = {'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data)
        now = datetime.datetime.now()
        rv = self.app.put('/status/{0}'.format(my_id), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        ads_after = [ds for ds in self._base_status.find({})]
        assert len(ads_after) == 1
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['status']['status'] == 'SUCCESS'
        assert res['status']['details'] == data['details']
        assert res['status']['last'] == True
        time_diff = datetime.datetime.strptime(res['status']['on'], '%Y-%m-%d %H:%M:%S') - now
        seconds = time_diff.days * 86400 + time_diff.seconds
        assert seconds < 2
        assert res['status']['test_id'] == my_id
#        assert res['status']['comment'] == ''
        print(res)
        print(res['status']['_id'])
        ds_after = self._base_status.find_one({'_id': ObjectId(res['status']['_id'])})
        assert ds_after['test_id'] == my_id
        test_after = self._base_test.find_one({'_id': my_id})
        assert test_after['last_seen'] == res['status']['on']
        assert test_after['type'] == data['type']

    def test_get_1_status(self):
        my_id = str(uuid.uuid4())
        rv = self.app.get('/status/{0}'.format(my_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['status']['status'] == 'UNKNOWN'
        assert res['status']['details'] == {}
        assert res['status']['last'] == True
        assert res['status']['test_id'] == my_id
#        assert res['status']['comment'] == ''
        res = json.loads(rv.data.decode('utf-8'))
        data = {'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data)
        rv = self.app.put('/status/{0}'.format(my_id), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        rv = self.app.get('/status/{0}'.format(my_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['status']['status'] == 'SUCCESS'
        assert res['status']['details'] == data['details']
        assert res['status']['last'] == True
        assert res['status']['test_id'] == my_id
#        assert res['status']['comment'] == ''
        self._base_status.remove({'test_id': my_id})
        rv = self.app.get('/status/{0}'.format(my_id))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        assert res['result'] == 'Success'
        assert res['status']['status'] == 'UNKNOWN'
        assert res['status']['details'] == {}
        assert res['status']['last'] == True
        assert res['status']['test_id'] == my_id
#        assert res['status']['comment'] == ''

    def test_save_get_n_status(self):
        my_id1 = str(uuid.uuid4())
        data1 = {'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.put('/status/{0}'.format(my_id1), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        data1 = {'status': 'FAILURE', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.put('/status/{0}'.format(my_id1), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        data1 = {'status': 'SUCCESS', 'details': {'browser': 'last', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data1)
        rv = self.app.put('/status/{0}'.format(my_id1), headers=json_query['headers'], data=json_query['json'])
        assert rv.status_code == 200
        my_id2 = str(uuid.uuid4())
        data = {'status': 'SUCCESS', 'details': {'browser': 'Chrome', 'environment': 'master'}, 'type': 'test_tool'}
        json_query = prepare_json_query(data)
        rv2 = self.app.put('/status/{0}'.format(my_id2), headers=json_query['headers'], data=json_query['json'])
        assert rv2.status_code == 200
        ads_after1 = [ds for ds in self._base_status.find({'test_id': my_id1})]
        assert len(ads_after1) == 3
        ads_after1 = [ds for ds in self._base_status.find({'test_id': my_id1, 'last': True})]
        assert len(ads_after1) == 1
        atest_after = [at for at in self._base_test.find({})]
        assert len(atest_after) == 2
        rv = self.app.get('/status/{0}'.format(my_id1))
        assert rv.status_code == 200
        res = json.loads(rv.data.decode('utf-8'))
        print(res)
        assert res['status']['_id'] == str(ads_after1[0]['_id'])
        assert res['status']['details']['browser'] == data1['details']['browser']
