import datetime

from . import Base
from .TestType import TestType

class Index:
    collection = 'test_index'
    _test_type = None
    _field = None
    _values = None

    def __init__(self, test_type=None, field=None, values=[]):
        self._test_type = test_type
        self._field = field
        self._values = values

    def __repr__(self):
        return '<Index {0} ({1}) : {2} values>'.format(self._field, self._test_type, len(self._values))

    def to_dict(self):
        dict_of_self = {}
        if self._test_type is not None:
            dict_of_self['type'] = self._test_type
        if self._field is not None:
            dict_of_self['field'] = self._field
        if self._values is not None:
            dict_of_self['values'] = self._values
        return dict_of_self

    @staticmethod
    def from_dict(index_dict):
        index = Index()
        if index_dict['type'] is not None:
            index._test_type = index_dict['type']
        if index_dict['field'] is not None:
            index._field = index_dict['field']
        if index_dict['values'] is not None:
            index._values = index_dict['values']
        return index

    @staticmethod
    def index(status):
        if status._details is not None:
            test_type = status._type
            fields = [key for key in status._details]
            for field in fields:
                current_index = Index(test_type=test_type, field=field, values=[])
                index_existing = current_index.get()
                if index_existing is not None:
                    current_index = index_existing
                if status._details[field] not in current_index._values:
                    current_index._values.append(status._details[field])
                    current_index.save()

    def get(self):
        query_filter = self.to_dict()
        if 'values' in query_filter:
            query_filter.pop('values')
        res = Base.Base().get_one(self.collection, query_filter)
        return Index.from_dict(res) if res is not None else None

    def save(self):
        index_id = "{0}-{1}".format(self._test_type, self._field)
        Base.Base().upsert_by_id(self.collection, index_id, self.to_dict())
