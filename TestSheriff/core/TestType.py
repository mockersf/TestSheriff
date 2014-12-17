import datetime

from . import Base


class TestType:
    collection = 'test_type'
    _test_type = 'type'
    _doc_fields = 'doc_fields'

    def __init__(self, test_type=None, doc_fields=None):
        self._test_type = test_type
        self._doc_fields = doc_fields

    def __repr__(self):
        return '<TestType {0} ({1})>'.format(self._test_type, self._doc_fields)

    def to_dict(self):
        dict_of_self = {}
        if self._test_type is not None:
            dict_of_self[TestType._test_type] = self._test_type
        if self._doc_fields is not None:
            dict_of_self[TestType._doc_fields] = self._doc_fields
        return dict_of_self

    @staticmethod
    def from_dict(test_type_dict):
        test_type = TestType()
        if test_type_dict[TestType._test_type] is not None:
            test_type._test_type = test_type_dict[TestType._test_type]
        if test_type_dict[TestType._doc_fields] is not None:
            test_type._doc_fields = test_type_dict[TestType._doc_fields]
        return test_type

    @staticmethod
    def from_status(status):
        test_type = status._type
        doc_fields = None
        if status._details is not None:
            doc_fields = [key for key in status._details]
        return TestType(test_type, doc_fields)

    def save(self):
        Base.Base().upsert_by_id(self.collection, self._test_type, self.to_dict())

    def get_all(self, additional_filter=None):
        query_filter = self.to_dict()
        if additional_filter is not None:
            query_filter.update(additional_filter)
        return [TestType.from_dict(btt) for btt in Base.Base().get_all(self.collection, query_filter)]

    def get_one(self):
        query_filter = self.to_dict()
        res = Base.Base().get_one(self.collection, query_filter)
        return TestType.from_dict(res) if res is not None else None
