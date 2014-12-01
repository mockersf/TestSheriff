import os, sys
import uuid
import datetime
import random
import time

def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_index(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'
        from core.Index import Index
        Base.Base().get_base()[Index.collection].drop()

    def teardown_method(self, method):
        from core import Base
        from core.Index import Index
        Base.Base().get_base()[Index.collection].drop()

    def test_repr_getter_setter(self):
        from core.Index import Index
        my_type = str(uuid.uuid4())
        field = str(uuid.uuid4())
        index = Index(my_type, field)
        assert '{0}'.format(index) == '<Index {0} ({1}) : 0 values>'.format(field, my_type)
        assert index.to_dict() == {'type': my_type, 'field': field, 'values': []}
        index._values = ['a', 'b', 'c']
        assert '{0}'.format(index) == '<Index {0} ({1}) : 3 values>'.format(field, my_type)
        index2 = Index.from_dict(index.to_dict())
        assert index2.to_dict() == index.to_dict()

    def test_save(self):
        from core.Index import Index
        from core.Base import Base
        my_type = str(uuid.uuid4())
        field = str(uuid.uuid4())
        values = ['a', 'b', 'c']
        index = Index(my_type, field, values)
        index.save()
        ast = Base().get_all(Index.collection, {})
        assert len(ast) == 1
        assert ast[0]['type'] == my_type
        assert ast[0]['field'] == field
        assert ast[0]['values'] == values
        index2 = Index(my_type, field)
        assert index2._values == []
        index2 = index2.get()
        assert index2._values == values

    def test_index(self):
        from core.Index import Index
        from core.Status import Status
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        field1 = 'browser'
        details1 = {field1: 'Firefox'}
        status1 = Status(test_id, test_type, test_status, details=details1)
        details2 = {field1: 'Chrome'}
        status2 = Status(test_id, test_type, test_status, details=details2)
        field2 = 'environment'
        details3 = {field2: 'master'}
        status3 = Status(test_id, test_type, test_status, details=details3)
        Index.index(status1)
        ast = Base().get_all(Index.collection, {})
        assert len(ast) == 1
        assert ast[0]['type'] == test_type
        assert ast[0]['field'] == field1
        assert ast[0]['values'] == ['Firefox']
        Index.index(status2)
        ast = Base().get_all(Index.collection, {})
        assert len(ast) == 1
        assert sorted(ast[0]['values']) == sorted(['Chrome', 'Firefox'])
        Index.index(status3)
        ast = Base().get_all(Index.collection, {})
        assert len(ast) == 2
        ast = Base().get_all(Index.collection, {'field': 'browser'})
        assert len(ast) == 1
        assert sorted(ast[0]['values']) == sorted(['Chrome', 'Firefox'])
        ast = Base().get_all(Index.collection, {'field': 'environment'})
        assert len(ast) == 1
        assert ast[0]['values'] == ['master']

    def test_index_large_status(self):
        from core.Index import Index
        from core.Status import Status
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        field1 = 'browser'
        field2 = 'environment'
        details1 = {field1: 'Firefox', field2: 'master'}
        status1 = Status(test_id, test_type, test_status, details=details1)
        Index.index(status1)
        details2 = {field1: 'Chrome', field2: 'master'}
        status2 = Status(test_id, test_type, test_status, details=details2)
        Index.index(status2)
        ast = Base().get_all(Index.collection, {'field': 'browser'})
        assert len(ast) == 1
        assert sorted(ast[0]['values']) == sorted(['Chrome', 'Firefox'])
        ast = Base().get_all(Index.collection, {'field': 'environment'})
        assert len(ast) == 1
        assert ast[0]['values'] == ['master']
