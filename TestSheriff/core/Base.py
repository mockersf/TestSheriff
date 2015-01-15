import pymongo
from bson import ObjectId

BASE_PREFIX = ''
BASE_HOST = 'localhost'
BASE_PORT = 27017

ASC = pymongo.ASCENDING
DESC = pymongo.DESCENDING


class TransformableCursor(object): # pylint: disable=too-few-public-methods
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

    def __delitem__(self, index):
        raise Exception('Deleting does not work on this cursor')

    def __setitem__(self, index, value):
        raise Exception('Setting does not work on this cursor')


class Base(object):
    _base = None

    def __init__(self):
        connection = pymongo.MongoClient(BASE_HOST, BASE_PORT)
        self._base = connection[BASE_PREFIX + 'TestSheriff']

    def get_base(self):
        return self._base

    def get_one(self, collection, query_filter=None):
        if query_filter is None:
            query_filter = {}
        if '_id' in query_filter and ObjectId.is_valid(query_filter['_id']):
            query_filter['_id'] = ObjectId(query_filter['_id'])
        return self._base[collection].find_one(query_filter)

    def get_all(self, collection, query_filter=None, # pylint: disable=R0913
                sort=None, page=None, nb_item=None):
        if query_filter is None:
            query_filter = {}
        items = self._base[collection].find(query_filter)
        if sort is not None:
            items.sort(sort)
        if page is not None and nb_item is not None and \
           page >= 0 and nb_item >= 0:
            items = items[page * nb_item:(page + 1) * nb_item]
        return TransformableCursor(items)

    def upsert_by_id(self, collection, object_id, object_to_update):
        res = self._base[collection].update({'_id': object_id},
                                            {'$set': object_to_update},
                                            upsert=True)
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
