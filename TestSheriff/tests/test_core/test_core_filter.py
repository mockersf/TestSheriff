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
