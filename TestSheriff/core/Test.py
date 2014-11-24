import datetime

from . import Base


class Test:
    _test_id = None
    _owner = None
    _type = None
    _last_seen = None

    def __init__(self, test_id=None, owner=None, test_type=None):
        self._test_id = test_id
        self._owner = owner
        self._type = test_type

    def __repr__(self):
        return '<Test {0} ({1}) by {2}>'.format(self._test_id, self._type, self._owner)

    def to_dict(self):
        dict_of_self = {}
        if self._test_id is not None:
            dict_of_self['test_id'] = self._test_id
        if self._type is not None:
            dict_of_self['type'] = self._type
        if self._owner is not None:
            dict_of_self['owner'] = self._owner
        if self._last_seen is not None:
            dict_of_self['last_seen'] = self._last_seen.strftime(Base.time_format)
        return dict_of_self

    def from_dict(self, test_dict):
        test = Test()
        if 'test_id' in test_dict:
            test._test_id = test_dict['test_id']
        if 'type' in test_dict:
            test._type = test_dict['type']
        if 'owner' in test_dict:
            test._owner = test_dict['owner']
        if 'last_seen' in test_dict:
            test._last_seen = datetime.datetime.strptime(test_dict['last_seen'], Base.time_format)
        return test

    def get_all(self):
        filter = self.to_dict()
        return Base.Base().get_all('test', filter)

    def get_one(self):
        filter = self.to_dict()
        res = Base.Base().get_one('test', filter)
        return self.from_dict(res) if res is not None else None

    def save(self):
        self._last_seen = datetime.datetime.now()
        self._last = True
        return Base.Base().upsert_by_id('test', self._test_id, self.to_dict())
