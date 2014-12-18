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
        from core import Base
        from core.Index import Index
        from core.Test import Test
        from core.Status import Status
        from core.TestType import TestType
        Base.Base().get_base()[Index.collection].drop()
        Base.Base().get_base()[Test.collection].drop()
        Base.Base().get_base()[Status.collection].drop()
        Base.Base().get_base()[TestType.collection].drop()

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
