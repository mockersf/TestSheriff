import pymongo
import bson

base_prefix = ''
base_host = 'localhost'
base_port = 27017

asc = pymongo.ASCENDING
desc = pymongo.DESCENDING


class TransformableCursor:
    _cursor = None
    _transform = None

    def __init__(self, cursor, transform=lambda o: o):
        self._cursor = cursor
        self._transform = transform

    def count(self):
        return self._cursor.count(with_limit_and_skip=False)

    def __len__(self):
        return self._cursor.count(with_limit_and_skip=True)

    def __iter__(self):
        for obj in self._cursor:
            yield self._transform(obj)

    def __getitem__(self, index):
        return self._transform(self._cursor[index])


class Base:
    _base = None

    def __init__(self):
        connection = pymongo.MongoClient(base_host, base_port)
        self._base = connection[base_prefix + 'TestSheriff']

    def get_base(self):
        return self._base

    def get_one(self, collection, query_filter={}):
        if '_id' in query_filter and bson.ObjectId.is_valid(query_filter['_id']):
            query_filter['_id'] = bson.ObjectId(query_filter['_id'])
        return self._base[collection].find_one(query_filter)

    def get_all(self, collection, query_filter={}, sort=None, page=None, nb=None):
        items = self._base[collection].find(query_filter)
        if sort is not None:
            items.sort(sort)
        if page is not None and nb is not None and page >= 0 and nb >= 0:
            items = items[page * nb:(page + 1) * nb]
        return TransformableCursor(items)

    def upsert_by_id(self, collection, object_id, object_to_update):
        res = self._base[collection].update({'_id': object_id}, {'$set': object_to_update}, upsert=True)
        return res['err'] is None

    def insert(self, collection, object_to_insert):
        res = self._base[collection].insert(object_to_insert)
        return res

    def update(self, collection, object_to_update, updated):
        res = self._base[collection].update(object_to_update, {'$set': updated})
        return res['err'] is None

    def remove_by_id(self, collection, object_id):
        res = self._base[collection].remove({'_id': object_id})
        return res['err'] is None
