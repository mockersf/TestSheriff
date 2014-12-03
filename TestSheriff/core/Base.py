import pymongo


base_prefix = ''
asc = pymongo.ASCENDING
desc = pymongo.DESCENDING

class Base:
    _base = None

    def __init__(self):
        connection = pymongo.MongoClient('localhost', 27017)
        self._base = connection[base_prefix + 'TestSheriff']

    def get_base(self):
        return self._base

    def get_one(self, collection, query_filter={}):
        return self._base[collection].find_one(query_filter)

    def get_all(self, collection, query_filter={}, sort=None):
        items = self._base[collection].find(query_filter)
        if sort is not None:
            items.sort(sort)
        return [item for item in items]

    def upsert_by_id(self, collection, object_id, object_to_update):
        res = self._base[collection].update({'_id': object_id}, {'$set': object_to_update}, upsert=True)
        return res['err'] is None

    def insert(self, collection, object_to_insert):
        res = self._base[collection].insert(object_to_insert)
        return res

    def update(self, collection, object_to_update, updated):
        res = self._base[collection].update(object_to_update, {'$set': updated})
        return res['err'] is None
