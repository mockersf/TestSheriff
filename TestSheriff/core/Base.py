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

    def get_one(self, collection, query_filter={}):
        return self._base[collection].find_one(query_filter)

    def get_all(self, collection, query_filter={}):
        return [item for item in self._base[collection].find(query_filter)]

    def upsert_by_id(self, collection, object_id, object_to_update):
        res = self._base[collection].update({'_id': object_id}, {'$set': object_to_update}, upsert=True)
        return res['err'] is None

    def insert(self, collection, object_to_insert):
        res = self._base[collection].insert(object_to_insert)
        return res

    def update(self, collection, object_to_update, updated):
        res = self._base[collection].update(object_to_update, {'$set': updated})
        return res['err'] is None
