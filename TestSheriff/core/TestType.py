from .Filter import Filter
from .CoreObject import CoreObject


class TestType(CoreObject):
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
        super(TestType, self).__init__()
        self._test_type = test_type
        self._doc_fields = doc_fields
        self._doc_fields_to_index = doc_fields_to_index
        self._purge = None
        self._run = None

    def __repr__(self):
        return '<TestType {0} ({1})>'.format(self._test_type, self._doc_fields)

    def to_dict(self):
        dict_of_self = super(TestType, self).to_dict()
        if self._purge is not None:
            dict_of_self[TestType._purge] = {'action': self._purge['action'],
                                             'condition': self._purge['condition'].to_dict()}
        if self._run is not None:
            dict_of_self[TestType._run] = {run: {'modifier': self._run[run]['modifier'],
                                                 'condition': self._run[run]['condition'].to_dict()}
                                           for run in self._run}
        return dict_of_self

    @classmethod
    def from_dict(cls, test_type_dict):
        test_type = super(TestType, cls).from_dict(test_type_dict)
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
        self.save_by_id(self._test_type)

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
