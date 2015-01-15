import datetime

from . import Base


class Test(object):
    collection = 'test'
    _test_id = 'test_id'
    _owner = 'owner'
    _type = 'type'
    _last_seen = 'last_seen'

    def __init__(self, test_id=None, owner=None, test_type=None):
        self._test_id = test_id
        self._owner = owner
        self._type = test_type
        self._last_seen = None

    def __repr__(self):
        return '<Test {0} ({1}) by {2}>'.format(self._test_id, self._type, self._owner)

    def to_dict(self):
        dict_of_self = {}
        if self._test_id is not None:
            dict_of_self[Test._test_id] = self._test_id
        if self._type is not None:
            dict_of_self[Test._type] = self._type
        if self._owner is not None:
            dict_of_self[Test._owner] = self._owner
        if self._last_seen is not None:
            dict_of_self[Test._last_seen] = self._last_seen
        return dict_of_self

    @staticmethod
    def from_dict(test_dict):
        test = Test()
        if Test._test_id in test_dict:
            test._test_id = test_dict[Test._test_id]
        if Test._type in test_dict:
            test._type = test_dict[Test._type]
        if Test._owner in test_dict:
            test._owner = test_dict[Test._owner]
        if Test._last_seen in test_dict:
            test._last_seen = test_dict[Test._last_seen]
        return test

    def get_all(self, additional_filter=None):
        query_filter = self.to_dict()
        if additional_filter is not None:
            query_filter.update(additional_filter)
        cursor = Base.Base().get_all(self.collection, query_filter)
        cursor._transform = lambda bt: Test.from_dict(bt) # pylint: disable=unnecessary-lambda
        return cursor

    def get_all_ownerless(self):
        additional_filter = {Test._owner: None}
        return self.get_all(additional_filter)

    def get_one(self):
        query_filter = self.to_dict()
        res = Base.Base().get_one(self.collection, query_filter)
        return Test.from_dict(res) if res is not None else None

    def save(self):
        self._last_seen = datetime.datetime.now()
        return Base.Base().upsert_by_id(self.collection, self._test_id, self.to_dict())
