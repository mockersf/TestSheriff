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
        test_type = TestType(my_type, doc)
        assert '{0}'.format(test_type) == '<TestType {0} ({1})>'.format(my_type, doc)
        assert test_type.to_dict() == {'type': my_type, 'doc_fields': doc}
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
