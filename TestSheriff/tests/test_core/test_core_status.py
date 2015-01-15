import os, sys
import uuid
import datetime
import random
import time
import bson

from tests import tools


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_status(object):
    def setup_method(self, method):
        from core import Base
        Base.BASE_PREFIX = 'test'

    def teardown_method(self, method):
        tools.db_drop()

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
        assert status.to_dict()['on'] == status._on.replace(microsecond=0)
        assert status.to_dict()['last'] == status._last
        assert status.to_dict()['details'] == status._details
        status2 = status.from_dict(status.to_dict())
        assert status2.to_dict() == status.to_dict()

    def test_save(self):
        from core.Status import Status
        from core.Test import Test
        from core.Index import Index
        from core.TestType import TestType
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status = random.choice(['SUCCESS', 'FAILURE'])
        test_type = str(uuid.uuid4())
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status = Status(test_id, test_type, test_status, details=details)
        TestType(test_type, doc_fields_to_index=['browser']).save()
        now = datetime.datetime.now()
        status.save()
        ast = Base().get_all(Status.collection, {})
        assert ast.count() == 1
        assert ast[0]['test_id'] == test_id
        assert ast[0]['status'] == test_status
        assert ast[0]['details'] == details
        assert ast[0]['type'] == test_type
        assert ast[0]['on'] < now + datetime.timedelta(seconds=1)
        at = Base().get_all(Test.collection, {})
        assert at.count() == 1
        assert at[0]['test_id'] == test_id
        assert at[0]['type'] == test_type
        assert at[0]['last_seen'] < ast[0]['on'] + datetime.timedelta(seconds=1)
        st = Base().get_one(Index.collection, {})
        assert st['type'] == test_type
        assert st['field'] == 'browser'
        assert st['values'] == [details['browser']]
        st = Base().get_one(TestType.collection, {})
        assert st['type'] == test_type
        assert st['doc_fields'] == ['browser']
        test_id = str(uuid.uuid4())
        test_status = 'TO_RERUN'
        test_type = str(uuid.uuid4())
        status = Status(test_id, test_type, test_status)
        now = datetime.datetime.now()
        status.save()
        st = Base().get_one(Status.collection, {'test_id': test_id})
        assert st['status'] == 'CUSTOM'
        assert st['details']['original_status'] == test_status

    def test_remove(self):
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
        status2.remove()
        ast = Base().get_all(Status.collection, {})
        assert ast.count() == 1
        assert ast[0]['test_id'] == test_id1

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
        assert ast.count() == 1
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
        assert ast.count() == 2
        ast = Base().get_all(Status.collection, {'last': False})
        assert ast.count() == 1
        assert ast[0]['status'] == 'FAILURE'
        ast = Base().get_all(Status.collection, {'last': True})
        assert ast.count() == 1
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
        assert at.count() == 1
        assert at[0]['test_id'] == test_id
        test_status2 = 'SUCCESS'
        status2 = Status(test_id, test_type, test_status2, details=details)
        status2.save_and_update()
        at = Base().get_all(Test.collection, {})
        assert at.count() == 1
        Base().upsert_by_id(Status.collection, bson.ObjectId(status1._id), {Status._on: datetime.datetime.now() - datetime.timedelta(seconds=3)})
        Base().upsert_by_id(Status.collection, bson.ObjectId(status2._id), {Status._on: datetime.datetime.now() - datetime.timedelta(seconds=3)})
        sl = Status(test_id).get_last()
        assert sl._status == 'SUCCESS'
        assert sl._test_id == test_id
        at = Base().get_all(Test.collection, {})
        assert at.count() == 1
        assert at[0]['last_seen'] > Status(base_id=status2._id).get()._on + datetime.timedelta(seconds=1)

    def test_list(self):
        from core.Status import Status
        from core import Base
        test_id1 = str(uuid.uuid4())
        test_status = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        test_type = str(uuid.uuid4())
        status1 = Status(test_id1, test_type, test_status, details=details)
        status1.save()
        Base.Base().upsert_by_id(Status.collection, bson.ObjectId(status1._id), {Status._on: datetime.datetime.now() - datetime.timedelta(seconds=1)})
        test_id2 = str(uuid.uuid4())
        status2 = Status(test_id2, test_type, test_status, details=details)
        status2.save()
        ast = Status.list(sort=[('on', Base.DESC)])
        assert len(ast) == 2
        assert ast[0].to_dict() == Status(base_id=status2._id).get().to_dict()
        assert ast[1].to_dict() == Status(base_id=status1._id).get().to_dict()
        ast = Status.list(sort=[('on', Base.ASC)])
        assert len(ast) == 2
        assert ast[0].to_dict() == Status(base_id=status1._id).get().to_dict()
        assert ast[1].to_dict() == Status(base_id=status2._id).get().to_dict()

    def test_list_page(self):
        from core.Status import Status
        from core import Base
        test_id1 = str(uuid.uuid4())
        test_status = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        test_type = str(uuid.uuid4())
        nb = 10
        statuses = {}
        for i in range(nb):
            status = Status(test_id1, test_type, test_status, details=details)
            status.save()
            Base.Base().upsert_by_id(Status.collection, bson.ObjectId(status._id), {Status._on: datetime.datetime.now() - datetime.timedelta(seconds=nb - i + 1)})
            statuses[i] = status
        ast = Status.list(sort=[('on', Base.ASC)], page=1, nb=2)
        assert len(ast) == 2
        assert ast[0].to_dict() == Status(base_id=statuses[2]._id).get().to_dict()
        assert ast[1].to_dict() == Status(base_id=statuses[3]._id).get().to_dict()
        ast = Status.list(sort=[('on', Base.DESC)], page=2, nb=3)
        assert len(ast) == 3
        assert ast[0].to_dict() == Status(base_id=statuses[3]._id).get().to_dict()
        assert ast[1].to_dict() == Status(base_id=statuses[2]._id).get().to_dict()
        assert ast[2].to_dict() == Status(base_id=statuses[1]._id).get().to_dict()

    def test_get(self):
        from core.Status import Status
        test_id = str(uuid.uuid4())
        test_status = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        test_type = str(uuid.uuid4())
        status = Status(test_id, test_type, test_status, details=details)
        status.save()
        status_jid = Status(base_id=status._id)
        status_get = status_jid.get()
        assert status_get.to_dict() == status.to_dict()

    def test_add_unknown_if_none_exists(self):
        from core.Status import Status
        test_id = str(uuid.uuid4())
        status = Status(test_id)
        assert status.get() == None
        status.add_unknown_if_none_exist()
        status_saved = Status(test_id).get()
        assert status_saved._id != None
        assert status_saved._last == True
        assert status_saved._status == 'UNKNOWN'

    def test_should_i_run_default(self):
        from core.Status import Status
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        test_type = str(uuid.uuid4())
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        test_id2 = str(uuid.uuid4())
        test_status2 = 'SUCCESS'
        status2 = Status(test_id2, test_type, test_status2, details=details)
        status2.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        test_status3 = 'SUCCESS'
        status3 = Status(test_id, test_type, test_status3, details=details)
        status3.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == True

    def test_should_i_run_custom_any(self):
        from core.Status import Status
        from core.TestType import TestType
        test_type = str(uuid.uuid4())
        tt = TestType(test_type)
        tt.add_run_type('default', 'ANY', {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'UNKNOWN'})
        tt.save()
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        test_id2 = str(uuid.uuid4())
        test_status2 = 'SUCCESS'
        status2 = Status(test_id2, test_type, test_status2, details=details)
        status2.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        test_status3 = 'SUCCESS'
        status3 = Status(test_id, test_type, test_status3, details=details)
        status3.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        status4 = Status(str(uuid.uuid4()))
        status4.add_unknown_if_none_exist()
        res = status4.should_i_run()
        assert res == True

    def test_should_i_run_custom_all(self):
        from core.Status import Status
        from core.TestType import TestType
        test_type = str(uuid.uuid4())
        tt = TestType(test_type)
        tt.add_run_type('default', 'ALL', {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'SUCCESS'})
        tt.save()
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        test_id2 = str(uuid.uuid4())
        test_status2 = 'SUCCESS'
        status2 = Status(test_id2, test_type, test_status2, details=details)
        status2.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        test_status3 = 'SUCCESS'
        status3 = Status(test_id, test_type, test_status3, details=details)
        status3.save_and_update()
        res = Status(test_id).should_i_run()
        assert res == False
        res = Status(test_id2).should_i_run()
        assert res == True
        status2 = Status(test_id2, test_type, test_status2, details=details)
        status2.save_and_update()
        res = Status(test_id2).should_i_run()
        assert res == True

    def test_purge(self):
        from core.Status import Status
        from core.Base import Base
        test_id = str(uuid.uuid4())
        test_status1 = 'FAILURE'
        details = {'browser': random.choice(['Firefox', 'Chrome'])}
        test_type = str(uuid.uuid4())
        status1 = Status(test_id, test_type, test_status1, details=details)
        status1.save_and_update()
        ast = Base().get_all(Status.collection, {})
        Base().upsert_by_id(Status.collection, bson.ObjectId(status1._id), {Status._on: datetime.datetime.now() - datetime.timedelta(days=8)})
        ast = Base().get_all(Status.collection, {})
        test_id2 = str(uuid.uuid4())
        test_status2 = 'SUCCESS'
        status2 = Status(test_id2, test_type, test_status2, details=details)
        status2.save_and_update()
        test_status3 = 'SUCCESS'
        status3 = Status(test_id, test_type, test_status3, details=details)
        status3.save_and_update()
        res = status3.purge()
        assert res['nb_removed'] == 1
        ast = Base().get_all(Status.collection, {})
        assert ast.count() == 2
        assert sorted([str(st['_id']) for st in ast]) == sorted([status2._id, status3._id])
