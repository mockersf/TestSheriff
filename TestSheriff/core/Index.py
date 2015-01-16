from .TestType import TestType
from .CoreObject import CoreObject


class Index(CoreObject):
    collection = 'test_index'
    _test_type = 'type'
    _field = 'field'
    _values = 'values'

    def __init__(self, test_type=None, field=None, values=None):
        super(Index, self).__init__()
        self._test_type = test_type
        self._field = field
        self._values = values

    def __repr__(self):
        return '<Index {0} ({1}) : {2} values>'\
            .format(self._field, self._test_type,
                    len(self._values) if self._values is not None else 0)

    @staticmethod
    def index(status):
        if status._details is not None:
            test_type = TestType.get_one({TestType._test_type: status._type})
            if test_type._doc_fields_to_index is not None:
                fields = [key for key in status._details if key in test_type._doc_fields_to_index]
                for field in fields:
                    current_index = Index(test_type=test_type._test_type, field=field, values=[])
                    index_existing = current_index.get()
                    if index_existing is not None:
                        current_index = index_existing
                    if status._details[field] not in current_index._values:
                        current_index._values.append(status._details[field])
                        current_index.save()

    def get(self):
        query_filter = self.to_dict()
        if Index._values in query_filter:
            query_filter.pop(Index._values)
        return Index.get_one(query_filter)

    def save(self):
        index_id = "{0}-{1}".format(self._test_type, self._field)
        return super(Index, self).save_by_id(index_id)
