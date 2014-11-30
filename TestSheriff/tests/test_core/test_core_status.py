import os, sys
import uuid
import datetime
import random
import time

def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_status(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'

    def teardown_method(self, method):
        from core import Base
        from core.Status import Status
        from core.Test import Test
        Base.Base().get_base()[Status.collection].drop()
        Base.Base().get_base()[Test.collection].drop()

    def test_repr_getter_setter(self):
        from core.Status import Status
        test_id = str(uuid.uuid4())
        test_status = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        status = Status(test_id, test_type, test_status)
        assert '{0}'.format(status) == '<Status {0} ({1}) : {2} on the {3}>'.format(test_id, test_type, test_status, None)
        assert status.to_dict() == {'test_id': test_id, 'status': test_status, 'type': test_type}
        status._on = datetime.datetime.now()
        status._last = True
        status._details = {'browser': random.choice(['Firefox', 'Chrome'])}
        assert status.to_dict()['on'] == status._on
        assert status.to_dict()['last'] == status._last
        assert status.to_dict()['details'] == status._details
        status2 = status.from_dict(status.to_dict())
        assert status2.to_dict() == status.to_dict()

    def test_save(self):
        from core.Status import Status
        from core.Test import Test
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status = Status(test_id, test_type, test_status, details=details)
        now = datetime.datetime.now()
        status.save()
        ast = Base().get_all(Status.collection, {})
        assert len(ast) == 1
        assert ast[0]['test_id'] == test_id
        assert ast[0]['status'] == test_status
        assert ast[0]['details'] == details
        assert ast[0]['type'] == test_type
        assert ast[0]['on'] < now + datetime.timedelta(seconds=1)
        at = Base().get_all(Test.collection, {})
        assert len(at) == 1
        assert at[0]['test_id'] == test_id
        assert at[0]['type'] == test_type
        assert at[0]['last_seen'] < ast[0]['on'] + datetime.timedelta(seconds=1)
        test_id = str(uuid.uuid4())
        test_status = 'TO_RERUN'
        test_type = str(uuid.uuid4())
        status = Status(test_id, test_type, test_status)
        now = datetime.datetime.now()
        status.save()
        st = Base().get_one(Status.collection, {'test_id': test_id})
        assert st['status'] == 'CUSTOM'
        assert st['details']['original_status'] == test_status

    def test_update_last(self):
        from core.Status import Status
        from core.Base import Base
        test_id1 = str(uuid.uuid4())
        test_status1 = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status1 = Status(test_id1, test_type, test_status1, details=details, last=True)
        status1.save()
        test_id2 = str(uuid.uuid4())
        test_status2 = random.choice(['SUCCESS', 'FAILURE'])
        status2 = Status(test_id2, test_type, test_status2, details=details, last=True)
        status2.save()
        st = Base().get_one(Status.collection, {})
        assert st['last'] == True
        status2.update_last()
        ast = Base().get_all(Status.collection, {'last': True})
        assert len(ast) == 1
        st = Base().get_one(Status.collection, {'test_id': test_id2})
        assert st['last'] == False

    def test_save_and_update(self):
        from core.Status import Status
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        test_type = str(uuid.uuid4())
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        st = Base().get_one(Status.collection, {})
        assert st['last'] == True
        test_status2 = 'SUCCESS'
        status2 = Status(test_id, test_type, test_status2, details=details)
        status2.save_and_update()
        ast = Base().get_all(Status.collection, {})
        assert len(ast) == 2
        ast = Base().get_all(Status.collection, {'last': False})
        assert len(ast) == 1
        assert ast[0]['status'] == 'FAILURE'
        ast = Base().get_all(Status.collection, {'last': True})
        assert len(ast) == 1
        assert ast[0]['status'] == 'SUCCESS'

    def test_get_last(self):
        from core.Status import Status
        from core.Test import Test
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        test_type = str(uuid.uuid4())
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        at = Base().get_all(Test.collection, {})
        assert len(at) == 1
        assert at[0]['test_id'] == test_id
        test_status2 = 'SUCCESS'
        status2 = Status(test_id, test_type, test_status2, details=details)
        status2.save_and_update()
        at = Base().get_all(Test.collection, {})
        assert len(at) == 1
        time.sleep(3)
        sl = Status(test_id).get_last()
        assert sl._status == 'SUCCESS'
        assert sl._test_id == test_id
        at = Base().get_all(Test.collection, {})
        assert len(at) == 1
        assert at[0]['last_seen'] > status2._on + datetime.timedelta(seconds=1)
