import datetime

from .CoreObject import CoreObject


class Test(CoreObject):
    collection = 'test'
    _test_id = 'test_id'
    _owner = 'owner'
    _type = 'type'
    _last_seen = 'last_seen'

    def __init__(self, test_id=None, owner=None, test_type=None):
        super(Test, self).__init__()
        self._test_id = test_id
        self._owner = owner
        self._type = test_type
        self._last_seen = None

    def __repr__(self):
        return '<Test {0} ({1}) by {2}>'.format(self._test_id, self._type, self._owner)

    def get_all_ownerless(self):
        query_filter = self.to_dict()
        query_filter[Test._owner] = None
        return Test.get_all(query_filter)

    def save(self):
        self._last_seen = datetime.datetime.now()
        return super(Test, self).save_by_id(self._test_id)
