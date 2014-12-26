import os, sys
import uuid
import datetime
import random
import time

def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_testtype(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'

    def teardown_method(self, method):
        from core import Base
        from core.TestType import TestType
        Base.Base().get_base()[TestType.collection].drop()

    def test_repr_getter_setter(self):
        from core.TestType import TestType
        my_type = str(uuid.uuid4())
        doc = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        doc_fields_to_index = [doc[0]]
        test_type = TestType(my_type, doc, doc_fields_to_index)
        assert '{0}'.format(test_type) == '<TestType {0} ({1})>'.format(my_type, doc)
        assert test_type.to_dict() == {'type': my_type, 'doc_fields': doc, 'doc_fields_to_index': [doc[0]]}
        test_type2 = TestType.from_dict(test_type.to_dict())
        assert test_type2.to_dict() == test_type.to_dict()

    def test_save(self):
        from core.TestType import TestType
        from core.Base import Base
        my_type = str(uuid.uuid4())
        doc = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type = TestType(my_type, doc)
        test_type.save()
        ast = Base().get_all(TestType.collection, {})
        assert len(ast) == 1
        assert ast[0]['type'] == my_type
        assert ast[0]['doc_fields'] == doc

    def test_from_status(self):
        from core.TestType import TestType
        from core.Status import Status
        test_id = str(uuid.uuid4())
        test_status = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status = Status(test_id, test_type, test_status, details=details)
        test_type_obj = TestType.from_status(status)
        assert test_type_obj._test_type == test_type
        assert test_type_obj._doc_fields == ['browser']
        assert test_type_obj._doc_fields_to_index == None
        assert test_type_obj._purge == None
        assert test_type_obj._run == None

    def test_get_all(self):
        from core.TestType import TestType
        from core.Base import Base
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type1 = TestType(my_type1, doc1)
        test_type1.save()
        my_type2 = str(uuid.uuid4())
        doc2 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type2 = TestType(my_type2, doc2)
        test_type2.save()
        types = TestType().get_all()
        assert len(types) == 2
        types = TestType(my_type2).get_all()
        assert len(types) == 1
        assert types[0]._doc_fields == doc2
        types = TestType().get_all(additional_filter={TestType._test_type: my_type1})
        assert len(types) == 1
        assert types[0]._doc_fields == doc1

    def test_get_one(self):
        from core.TestType import TestType
        from core.Base import Base
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type1 = TestType(my_type1, doc1)
        test_type1.save()
        my_type2 = str(uuid.uuid4())
        doc2 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type2 = TestType(my_type2, doc2)
        test_type2.save()
        type2 = TestType(my_type2).get_one()
        assert type2._doc_fields == doc2
        assert type2._test_type == my_type2
        type1 = TestType(my_type1).get_one()
        assert type1._doc_fields == doc1
        assert type1._test_type == my_type1

    def test_run(self):
        from core.TestType import TestType
        from core.Base import Base
        from core.Filter import Filter
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type = TestType(my_type1, doc1)
        assert test_type.run() == test_type._default_run
        assert test_type.run('default') == test_type._default_run
        modifier = str(uuid.uuid4())
        res = test_type.add_run_type('new', modifier, {'operator': 'EQUAL', 'field': 1, 'value': 1})
        assert res == False
        assert test_type.run('new') == None
        modifier = 'ANY'
        res = test_type.add_run_type('new', modifier, {'operator': 'EQUAL', 'field': 1, 'value': 1})
        assert res
        assert test_type.run('new')['modifier'] == 'ANY'
        assert test_type.run('new')['condition'].to_dict() == {'operator': 'EQUAL', 'field': 1, 'value': 1}
        assert test_type.run('default') == test_type._default_run
        modifier = 'ALL'
        res = test_type.add_run_type('default', modifier, {'operator': 'EQUAL', 'field': 2, 'value': 3})
        assert res
        assert test_type.run('default')['modifier'] == 'ALL'
        assert test_type.run('default')['condition'].to_dict() == {'operator': 'EQUAL', 'field': 2, 'value': 3}
        assert test_type.run('not_existing') == None

    def test_purge(self):
        from core.TestType import TestType
        from core.Base import Base
        from core.Filter import Filter
        my_type1 = str(uuid.uuid4())
        doc1 = [str(uuid.uuid4()), str(uuid.uuid4()), str(uuid.uuid4())]
        test_type = TestType(my_type1, doc1)
        assert test_type.purge() == test_type._default_purge
        assert test_type.set_purge('REMOVE', {'operator': str(uuid.uuid4()), 'field': 1, 'value': 1}) == False
        condition = {'operator': 'EQUAL', 'field': 1, 'value': 1}
        action = str(uuid.uuid4())
        res = test_type.set_purge(action, condition)
        assert res == False
        assert test_type.purge() == test_type._default_purge
        action = 'REMOVE'
        res = test_type.set_purge(action, condition)
        assert res
        assert test_type.to_dict()['purge']['action'] == action
        assert test_type.to_dict()['purge']['condition'] == condition
        test_type2 = TestType.from_dict(test_type.to_dict())
        assert test_type.purge()['action'] == 'REMOVE'
        assert test_type.purge()['condition'].to_dict() == condition
        assert test_type2.purge()['action'] == 'REMOVE'
        assert test_type2.purge()['condition'].to_dict() == condition
