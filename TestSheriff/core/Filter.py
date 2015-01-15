import datetime # pylint: disable=unused-import


class Filter(object):
    _operator = None
    _part1 = None
    _part2 = None
    operators_compound = ['OR', 'AND']
    operators_final = ['EQUAL', 'NOT EQUAL', 'LESSER THAN', 'GREATER THAN']

    def __init__(self, operator=None, part1=None, part2=None):
        self._operator = operator
        self._part1 = part1
        self._part2 = part2

    def __repr__(self):
        return '<filter {0} {1} {2}>'.format(self._part1, self._operator, self._part2)

    @staticmethod
    def from_dict(filter_dict):
        if not isinstance(filter_dict, dict):
            return False
        fdict = filter_dict
        if 'operator' not in fdict:
            return False
        if fdict['operator'] in Filter.operators_final:
            if 'field' in fdict and 'value' in fdict:
                return Filter(fdict['operator'], fdict['field'], fdict['value'])
        if fdict['operator'] in Filter.operators_compound:
            if 'part1' not in fdict or 'part2' not in fdict:
                return False
            part1 = False
            part2 = False
            if isinstance(fdict['part1'], dict):
                part1 = Filter.from_dict(fdict['part1'])
            if isinstance(fdict['part2'], dict):
                part2 = Filter.from_dict(fdict['part2'])
            if part1 and part2:
                return Filter(fdict['operator'], part1, part2)
        return False

    def to_dict(self):
        if self._operator in Filter.operators_final:
            return {'operator': self._operator, 'field': self._part1, 'value': self._part2}
        if self._operator in Filter.operators_compound:
            return {'operator': self._operator,
                    'part1': self._part1.to_dict(),
                    'part2': self._part2.to_dict()}

    def check_status(self, status):
        from .Status import Status
        if self._operator == 'OR':
            return self._part1.check_status(status) or self._part2.check_status(status)
        if self._operator == 'AND':
            return self._part1.check_status(status) and self._part2.check_status(status)
        try:
            condition = eval(self._part2)
        except NameError:
            condition = self._part2
        field_name = self._part1
        if field_name[:17] == 'Status._details[\'':
            value = status.to_dict()[Status._details][field_name[17:-2]]
        else:
            field = eval(field_name)
            if field not in status.to_dict():
                return False
            value = status.to_dict()[eval(field_name)]
        return_value = False
        if self._operator == 'EQUAL':
            return_value = value == condition
        if self._operator == 'NOT EQUAL':
            return_value = value != condition
        if self._operator == 'LESSER THAN':
            return_value = value < condition
        if self._operator == 'GREATER THAN':
            return_value = value > condition
        return return_value

    def check_statuses(self, status_list):
        status_list_filtered = []
        for status in status_list:
            if self.check_status(status):
                status_list_filtered.append(status)
        return status_list_filtered
