import os, sys
import uuid
import datetime
import random
import time

from tests import tools


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_index(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'

    def teardown_method(self, method):
        tools.db_drop()

    def test_repr_getter_setter(self):
        from core.Filter import Filter
        operator = str(uuid.uuid4())
        part1 = str(uuid.uuid4())
        part2 = str(uuid.uuid4())
        my_filter = Filter(operator, part1, part2)
        assert '{0}'.format(my_filter) == '<filter {0} {1} {2}>'.format(part1, operator, part2)

    def test_from_dict_errors(self):
        from core.Filter import Filter
        assert Filter.from_dict(str(uuid.uuid4())) == False
        assert Filter.from_dict({str(uuid.uuid4()): str(uuid.uuid4())}) == False
        assert Filter.from_dict({'operator': str(uuid.uuid4()), 'part1': 1, 'part2': 2}) == False

    def test_filter_equal(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'EQUAL', 'field': 'Status._status', 'value': 'SUCCESS'})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={})
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={})
        assert my_filter.check_status(s1) == False
        assert my_filter.check_status(s2) == True
        status_filter = my_filter.check_statuses([s1, s2])
        assert len(status_filter) == 1
        assert status_filter[0]._test_id == s2._test_id

    def test_filter_not_equal(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'NOT EQUAL', 'field': 'Status._status', 'value': 'SUCCESS'})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={})
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={})
        assert my_filter.check_status(s1) == True
        assert my_filter.check_status(s2) == False
        status_filter = my_filter.check_statuses([s1, s2])
        assert len(status_filter) == 1
        assert status_filter[0]._test_id == s1._test_id

    def test_filter_lesser_than(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'LESSER THAN', 'field': 'Status._on', 'value': 'datetime.datetime.now()'})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={})
        s1._on = datetime.datetime.now() - datetime.timedelta(seconds=5)
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={})
        s2._on = datetime.datetime.now() + datetime.timedelta(seconds=5)
        assert my_filter.check_status(s1) == True
        assert my_filter.check_status(s2) == False
        status_filter = my_filter.check_statuses([s1, s2])
        assert len(status_filter) == 1
        assert status_filter[0]._test_id == s1._test_id

    def test_filter_greater_than(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'GREATER THAN', 'field': 'Status._on', 'value': 'datetime.datetime.now() + datetime.timedelta(days=1)'})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={})
        s1._on = datetime.datetime.now() - datetime.timedelta(seconds=5)
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={})
        s2._on = datetime.datetime.now() + datetime.timedelta(days=1, seconds=5)
        assert my_filter.check_status(s1) == False
        assert my_filter.check_status(s2) == True
        status_filter = my_filter.check_statuses([s1, s2])
        assert len(status_filter) == 1
        assert status_filter[0]._test_id == s2._test_id

    def test_filter_details(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'EQUAL', 'field': 'Status._details[\'BROWSER\']', 'value': 'Firefox'})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={'BROWSER': 'Firefox'})
        s1._on = datetime.datetime.now() - datetime.timedelta(seconds=5)
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={'BROWSER': 'Chrome'})
        s2._on = datetime.datetime.now() + datetime.timedelta(seconds=5)
        assert my_filter.check_status(s1) == True
        assert my_filter.check_status(s2) == False
        status_filter = my_filter.check_statuses([s1, s2])
        assert len(status_filter) == 1
        assert status_filter[0]._test_id == s1._test_id

    def test_filter_and(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'AND',
                                      'part1': {'operator': 'EQUAL', 'field': 'Status._status', 'value': 'SUCCESS'},
                                      'part2': {'operator': 'EQUAL', 'field': 'Status._last', 'value': 'True'}})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={})
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={}, last=True)
        s3 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={})
        s4 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={}, last=True)
        assert my_filter.check_status(s1) == False
        assert my_filter.check_status(s2) == True
        assert my_filter.check_status(s3) == False
        assert my_filter.check_status(s4) == False
        status_filter = my_filter.check_statuses([s1, s2, s3, s4])
        assert len(status_filter) == 1
        assert status_filter[0]._test_id == s2._test_id

    def test_filter_or(self):
        from core.Filter import Filter
        from core.Status import Status
        my_filter = Filter.from_dict({'operator': 'OR',
                                      'part1': {'operator': 'EQUAL', 'field': 'Status._status', 'value': 'SUCCESS'},
                                      'part2': {'operator': 'EQUAL', 'field': 'Status._last', 'value': 'True'}})
        assert my_filter != False
        s1 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={})
        s2 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={}, last=True)
        s3 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'SUCCESS', details={})
        s4 = Status(str(uuid.uuid4()), str(uuid.uuid4()), 'FAILURE', details={}, last=True)
        assert my_filter.check_status(s1) == False
        assert my_filter.check_status(s2) == True
        assert my_filter.check_status(s3) == True
        assert my_filter.check_status(s4) == True
        status_filter = my_filter.check_statuses([s1, s2, s3, s4])
        assert len(status_filter) == 3
        assert sorted([sf._test_id for sf in status_filter]) == sorted([s2._test_id, s3._test_id, s4._test_id])
