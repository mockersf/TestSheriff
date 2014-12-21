import datetime

from . import Base


class TestType:
    collection = 'test_type'
    _test_type = 'type'
    _doc_fields = 'doc_fields'
    _doc_fields_to_index = 'doc_fields_to_index'
    _purge = 'purge'
    _run = 'run'
    _default_purge = [{'field': 'Status._on', 'operator': 'before', 'value': 'datetime.datetime.now() - datetime.timedelta(days=7)'},
                      {'field': 'Status._last', 'operator': 'not equal', 'value': 'True'}]
    _default_run = {'modifier': 'ANY',
                    'condition':
                           {'operator': 'AND',
                            'part1': {'field': 'Status._last', 'operator': 'EQUAL', 'value': 'True'},
                            'part2': {'operator': 'OR',
                                      'part1': {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'SUCCESS'},
                                      'part2': {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'UNKNOWN'},
                                      },
                            }
                    }

    def __init__(self, test_type=None, doc_fields=None, doc_fields_to_index=None, purge=None, run=None):
        self._test_type = test_type
        self._doc_fields = doc_fields
        self._doc_fields_to_index = doc_fields_to_index
        self._purge = purge
        self._run = run

    def __repr__(self):
        return '<TestType {0} ({1})>'.format(self._test_type, self._doc_fields)

    def to_dict(self):
        dict_of_self = {}
        if self._test_type is not None:
            dict_of_self[TestType._test_type] = self._test_type
        if self._doc_fields is not None:
            dict_of_self[TestType._doc_fields] = self._doc_fields
        if self._doc_fields_to_index is not None:
            dict_of_self[TestType._doc_fields_to_index] = self._doc_fields_to_index
        if self._purge is not None:
            dict_of_self[TestType._purge] = self._purge
        if self._run is not None:
            dict_of_self[TestType._run] = self._run
        return dict_of_self

    @staticmethod
    def from_dict(test_type_dict):
        test_type = TestType()
        if TestType._test_type in test_type_dict:
            test_type._test_type = test_type_dict[TestType._test_type]
        if TestType._doc_fields in test_type_dict:
            test_type._doc_fields = test_type_dict[TestType._doc_fields]
        if TestType._doc_fields_to_index in test_type_dict:
            test_type._doc_fields_to_index = test_type_dict[TestType._doc_fields_to_index]
        if TestType._purge in test_type_dict:
            test_type._purge = test_type_dict[TestType._purge]
        if TestType._run in test_type_dict:
            test_type._run = test_type_dict[TestType._run]
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

    def run(self, run_type='default'):
        if self._run is not None and run_type in self._run:
            return self._run[run_type]
        if run_type == 'default':
            return self._default_run
        return None
