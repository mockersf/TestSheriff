import datetime
import bson

from . import Base
from .Test import Test
from .TestType import TestType
from .Index import Index


statuses = ['SUCCESS', 'FAILURE', 'UNKNOWN', 'CUSTOM', 'DEPRECATED']


class Status:
    collection = 'status'
    _test_id = 'test_id'
    _type = 'type'
    _on = 'on'
    _status = 'status'
    _details = 'details'
    _last = 'last'
    _id = '_id'


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
            dict_of_self[Status._test_id] = self._test_id
        if self._type is not None:
            dict_of_self[Status._type] = self._type
        if self._on is not None:
            dict_of_self[Status._on] = self._on.replace(microsecond=0)
        if self._status is not None:
            dict_of_self[Status._status] = self._status
        if self._details is not None:
            dict_of_self[Status._details] = self._details
        if self._last is not None:
            dict_of_self[Status._last] = self._last
        if self._id is not None:
            dict_of_self[Status._id] = self._id
        return dict_of_self

    @staticmethod
    def from_dict(status_dict):
        status = Status()
        if Status._test_id in status_dict:
            status._test_id = status_dict[Status._test_id]
        if Status._type in status_dict:
            status._type = status_dict[Status._type]
        if Status._on in status_dict:
            status._on = status_dict[Status._on]
        if Status._status in status_dict:
            status._status = status_dict[Status._status]
        if Status._details in status_dict:
            status._details = status_dict[Status._details]
        if Status._last in status_dict:
            status._last = status_dict[Status._last]
        if Status._id in status_dict:
            status._id = str(status_dict[Status._id])
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
        query_filter[Status._last] = True
        res = Base.Base().get_one(self.collection, query_filter)
        return Status.from_dict(res) if res is not None else None

    def get(self):
        query_filter = self.to_dict()
        res = Base.Base().get_one(self.collection, query_filter)
        return Status.from_dict(res) if res is not None else None

    def update_last(self):
        Base.Base().update(self.collection, {Status._test_id: self._test_id, Status._last: True}, {Status._last: False})

    def save_and_update(self):
        self.update_last()
        self._last = True
        self.save()

    def remove(self):
        Base.Base().remove_by_id(self.collection, bson.ObjectId(self._id))

    def should_i_run(self, run_type='default'):
        tt = TestType.from_status(self).get_one()
        run = tt.run(run_type)
        if run is None:
            return None
        condition = run['condition']
        modifier = run['modifier']
        status_list = Status.list({Status._test_id: self._test_id})
        status_list_filtered = condition.check_statuses(status_list)
        if modifier == 'ANY':
            return len(status_list_filtered) != 0
        if modifier == 'ALL':
            return len(status_list_filtered) == len(status_list)

    def purge(self):
        tt = TestType.from_status(self).get_one()
        if tt is None:
            return {'nb_removed': 0}
        run = tt.purge()
        condition = run['condition']
        action = run['action']
        status_list = Status.list({Status._test_id: self._test_id})
        status_list_filtered = condition.check_statuses(status_list)
        if action == 'REMOVE':
            for status in status_list_filtered:
                status.remove()
            return {'nb_removed': len(status_list_filtered)}

    def add_unknown_if_none_exist(self):
        last = self.get_last()
        if last is None:
            self._last = True
            self._status = 'UNKNOWN'
            self._on = datetime.datetime.now()
            self._id = str(Base.Base().insert(self.collection, self.to_dict()))
