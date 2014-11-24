import pymongo

time_format = '%Y-%m-%d %H:%M:%S'

base_prefix = ''

class Base:
    _base = None

    def __init__(self):
        connection = pymongo.MongoClient('localhost', 27017)
        self._base = connection[base_prefix + 'TestSheriff']

    def get_base(self):
        return self._base

    def get_one(self, collection, filter={}):
        return self._base[collection].find_one(filter)

    def get_all(self, collection, filter={}):
        return [item for item in self._base[collection].find(filter)]

    def upsert_by_id(self, collection, object_id, object):
        res = self._base[collection].update({'_id': object_id}, {'$set': object}, upsert=True)
        return res['err'] is None

    def insert(self, collection, object):
        res = self._base[collection].insert(object)
        return res

    def update(self, collection, a, b):
        res = self._base[collection].update(a, {'$set': b})
        return res['err'] is None
