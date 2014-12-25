
class Filter:
    _operator = None
    _part1 = None
    _part2 = None
    operators = ['OR', 'AND', 'EQUAL']

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
        fd = filter_dict
        if 'operator' not in fd:
            return False
        if fd['operator'] in ['EQUAL']:
            if 'field' in fd and 'value' in fd:
                return Filter(fd['operator'], fd['field'], fd['value'])
        if fd['operator'] in ['AND', 'OR']:
            if 'part1' not in fd or 'part2' not in fd:
                return False
            p1 = False
            p2 = False
            if isinstance(fd['part1'], dict):
                p1 = Filter.from_dict(fd['part1'])
            if isinstance(fd['part2'], dict):
                p2 = Filter.from_dict(fd['part2'])
            if p1 and p2:
                return Filter(fd['operator'], p1, p2)
        return False

    def to_dict(self):
        if self._operator in ['EQUAL']:
            return {'operator': self._operator, 'field': self._part1, 'value': self._part2}
        if self._operator in ['AND', 'OR']:
            return {'operator': self._operator, 'part1': self._part1.to_dict(), 'part2': self._part2.to_dict()}

    def check_status(self, status):
        from .Status import Status
        if self._operator == 'OR':
            return self._part1.check_status(status) or self._part2.check_status(status)
        if self._operator == 'AND':
            return self._part1.check_status(status) and self._part2.check_status(status)
        try:
            condition = eval(self._part2)
        except:
            condition = self._part2
        field_name = eval(self._part1)
        if self._operator == 'EQUAL':
            return status.to_dict()[field_name] == condition
