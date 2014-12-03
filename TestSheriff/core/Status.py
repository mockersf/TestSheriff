import datetime

from . import Base
from .Test import Test
from .TestType import TestType
from .Index import Index


statuses = ['SUCCESS', 'FAILURE', 'UNKNOWN', 'CUSTOM', 'DEPRECATED']


class Status:
    collection = 'status'
    _test_id = None
    _type = None
    _on = None
    _status = None
    _details = None
    _last = None
    _id = None


    def __init__(self, test_id=None, test_type=None, status=None, on=None,
                 details=None, last=None, base_id=None):
        self._test_id = test_id
        self._type = test_type
        self._on = on
        self._status = status
        self._details = details
        self._last = last
        self._id = base_id

    def __repr__(self):
        return '<Status {0} ({1}) : {2} on the {3}>'\
                    .format(self._test_id, self._type, self._status, self._on)

    def to_dict(self):
        dict_of_self = {}
        if self._test_id is not None:
            dict_of_self['test_id'] = self._test_id
        if self._type is not None:
            dict_of_self['type'] = self._type
        if self._on is not None:
            dict_of_self['on'] = self._on.replace(microsecond=0)
        if self._status is not None:
            dict_of_self['status'] = self._status
        if self._details is not None:
            dict_of_self['details'] = self._details
        if self._last is not None:
            dict_of_self['last'] = self._last
        if self._id is not None:
            dict_of_self['_id'] = self._id
        return dict_of_self

    @staticmethod
    def from_dict(status_dict):
        status = Status()
        if 'test_id' in status_dict:
            status._test_id = status_dict['test_id']
        if 'type' in status_dict:
            status._type = status_dict['type']
        if 'on' in status_dict:
            status._on = status_dict['on']
        if 'status' in status_dict:
            status._status = status_dict['status']
        if 'details' in status_dict:
            status._details = status_dict['details']
        if 'last' in status_dict:
            status._last = status_dict['last']
        if '_id' in status_dict:
            status._id = str(status_dict['_id'])
        return status

    @staticmethod
    def list(query_filter={}, sort=None):
        return [Status.from_dict(obj) for obj in Base.Base().get_all(Status.collection, query_filter, sort)]

    def save(self):
        Test(test_id=self._test_id, test_type=self._type).save()
        TestType.from_status(self).save()
        Index.index(self)
        self._on = datetime.datetime.now()
        if self._status not in statuses:
            if self._details is None:
                self._details = {}
            if 'original_status' not in self._details:
                self._details['original_status'] = self._status
            self._status = 'CUSTOM'
        self._id = str(Base.Base().insert(self.collection, self.to_dict()))

    def get_last(self):
        Test(test_id=self._test_id).save()
        query_filter = self.to_dict()
        query_filter['last'] = True
        res = Base.Base().get_one(self.collection, query_filter)
        return Status.from_dict(res) if res is not None else None

    def update_last(self):
        Base.Base().update(self.collection, {'test_id': self._test_id, 'last': True}, {'last': False})

    def save_and_update(self):
        self.update_last()
        self._last = True
        self.save()
