from . import Base
from .Filter import Filter


class TestType:
    collection = 'test_type'
    _test_type = 'type'
    _doc_fields = 'doc_fields'
    _doc_fields_to_index = 'doc_fields_to_index'
    _purge = 'purge'
    _run = 'run'
    _default_purge = [{'field': 'Status._on', 'operator': 'before', 'value': 'datetime.datetime.now() - datetime.timedelta(days=7)'},
                      {'field': 'Status._last', 'operator': 'not equal', 'value': 'True'}]
    _default_purge = {'action': 'REMOVE',
                      'condition': Filter.from_dict({'operator': 'AND',
                                                     'part1': {'field': 'Status._last', 'operator': 'NOT EQUAL', 'value': 'True'},
                                                     'part2': {'field': 'Status._on', 'operator': 'LESSER THAN', 'value': 'datetime.datetime.now() - datetime.timedelta(days=7)'}
                                                    })
                     }
    _default_run = {'modifier': 'ANY',
                    'condition': Filter.from_dict({'operator': 'AND',
                                                   'part1': {'field': 'Status._last', 'operator': 'EQUAL', 'value': 'True'},
                                                   'part2': {'operator': 'OR',
                                                             'part1': {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'SUCCESS'},
                                                             'part2': {'field': 'Status._status', 'operator': 'EQUAL', 'value': 'UNKNOWN'},
                                                            },
                                                  })
                   }
    modifiers = ['ANY', 'ALL']
    actions = ['REMOVE']

    def __init__(self, test_type=None, doc_fields=None, doc_fields_to_index=None):
        self._test_type = test_type
        self._doc_fields = doc_fields
        self._doc_fields_to_index = doc_fields_to_index
        self._purge = None
        self._run = None

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
            dict_of_self[TestType._purge] = {'action': self._purge['action'],
                                             'condition': self._purge['condition'].to_dict()}
        if self._run is not None:
            dict_of_self[TestType._run] = {run: {'modifier': self._run[run]['modifier'],
                                                 'condition': self._run[run]['condition'].to_dict()}
                                           for run in self._run}
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
            test_type._purge = {'action': test_type_dict[TestType._purge]['action'],
                                'condition': Filter.from_dict(test_type_dict[TestType._purge]['condition'])}
        if TestType._run in test_type_dict:
            run_dict = {run: {'modifier': test_type_dict[TestType._run][run]['modifier'],
                              'condition': Filter.from_dict(test_type_dict[TestType._run][run]['condition'])}
                        for run in test_type_dict[TestType._run]}
            test_type._run = run_dict
        return test_type

    @staticmethod
    def from_status(status):
        test_type = status._type
        doc_fields = None
        if status._details is not None:
            doc_fields = [key for key in status._details]
        return TestType(test_type, doc_fields)

    def save(self):
        Base.Base().upsert_by_id(self.collection, self._test_type,
                                 self.to_dict())

    def get_all(self, additional_filter=None):
        query_filter = self.to_dict()
        if additional_filter is not None:
            query_filter.update(additional_filter)
        cursor = Base.Base().get_all(self.collection, query_filter)
        cursor._transform = lambda btt: TestType.from_dict(btt)
        return cursor

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

    def add_run_type(self, run_type, modifier, condition):
        if modifier not in TestType.modifiers:
            return False
        if self._run is None:
            self._run = {}
        condition_filter = Filter.from_dict(condition)
        if not condition_filter:
            return False
        self._run[run_type] = {'modifier': modifier,
                               'condition': condition_filter}
        self.save()
        return True

    def purge(self):
        if self._purge is not None:
            return self._purge
        return self._default_purge

    def set_purge(self, action, condition):
        if action not in TestType.actions:
            return False
        condition_filter = Filter.from_dict(condition)
        if not condition_filter:
            return False
        self._purge = {'action': action, 'condition': condition_filter}
        self.save()
        return True
