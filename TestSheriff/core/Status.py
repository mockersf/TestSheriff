import datetime
import bson

from . import Base
from .Test import Test
from .TestType import TestType
from .Index import Index
from .CoreObject import CoreObject


STATUSES = ['SUCCESS', 'FAILURE', 'UNKNOWN', 'CUSTOM', 'DEPRECATED']


class Status(CoreObject):
    collection = 'status'
    _test_id = 'test_id'
    _type = 'type'
    _on = 'on'
    _status = 'status'
    _details = 'details'
    _last = 'last'
    _id = '_id'


    def __init__(self, test_id=None, test_type=None, status=None, on=None, # pylint: disable=too-many-arguments
                 details=None, last=None, base_id=None):
        super(Status, self).__init__()
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
        dict_of_self = super(Status, self).to_dict()
        if self._on is not None:
            dict_of_self[Status._on] = self._on.replace(microsecond=0)
        return dict_of_self

    @classmethod
    def from_dict(cls, status_dict):
        status = super(Status, cls).from_dict(status_dict)
        if Status._id in status_dict:
            status._id = str(status_dict[Status._id])
        return status

    @staticmethod
    def list(query_filter=None, sort=None, page=None, nb_item=None):
        return Status.get_all(query_filter, sort, page, nb_item)

    def save(self):
        Test(test_id=self._test_id, test_type=self._type).save()
        TestType.from_status(self).save()
        Index.index(self)
        self._on = datetime.datetime.now()
        if self._status not in STATUSES:
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
        Base.Base().update(self.collection, {Status._test_id: self._test_id, Status._last: True},
                           {Status._last: False})

    def save_and_update(self):
        self.update_last()
        self._last = True
        self.save()

    def remove(self):
        Base.Base().remove_by_id(self.collection, bson.ObjectId(self._id))

    def should_i_run(self, run_type='default'):
        test_type = TestType.get_one(TestType.from_status(self).to_dict())
        run = test_type.run(run_type)
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
        test_type = TestType.get_one(TestType.from_status(self).to_dict())
        if test_type is None:
            return {'nb_removed': 0}
        run = test_type.purge()
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
