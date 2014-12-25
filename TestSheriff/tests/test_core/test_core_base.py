import os, sys
import uuid


def setup_module(module):
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


class Test_core_base(object):
    def setup_method(self, method):
        from core import Base
        Base.base_prefix = 'test'
        self._base = Base.Base()
        self._test_collection_name = str(uuid.uuid4())
        self._test_collection = self._base.get_base()[self._test_collection_name]

    def teardown_method(self, method):
        self._test_collection.drop()

    def test_first_upsert_by_id(self):
        object_id = str(uuid.uuid4())
        res = self._base.upsert_by_id(self._test_collection_name, object_id, {})
        assert res
        aob = [ob for ob in self._test_collection.find({})]
        assert len(aob) == 1
        assert aob[0] == {'_id': object_id}

    def test_remove_by_id(self):
        object_id = str(uuid.uuid4())
        res = self._base.upsert_by_id(self._test_collection_name, object_id, {})
        aob = [ob for ob in self._test_collection.find({})]
        assert len(aob) == 1
        res = self._base.remove_by_id(self._test_collection_name, object_id)
        aob = [ob for ob in self._test_collection.find({})]
        assert len(aob) == 0

    def test_multiple_upsert_by_id(self):
        object_id1 = str(uuid.uuid4())
        object_id2 = str(uuid.uuid4())
        p1 = str(uuid.uuid4())
        p2 = str(uuid.uuid4())
        res = self._base.upsert_by_id(self._test_collection_name, object_id1, {'p': p1})
        assert res
        res = self._base.upsert_by_id(self._test_collection_name, object_id2, {'p': p1})
        assert res
        aob = [ob for ob in self._test_collection.find({})]
        assert len(aob) == 2
        res = self._base.upsert_by_id(self._test_collection_name, object_id1, {'p': p2})
        assert res
        aob = [ob for ob in self._test_collection.find({})]
        assert len(aob) == 2
        ob1 = self._test_collection.find_one({'_id': object_id1})
        ob2 = self._test_collection.find_one({'_id': object_id2})
        assert ob1['p'] == p2
        assert ob2['p'] == p1

    def test_get_one(self):
        object_id = str(uuid.uuid4())
        p = str(uuid.uuid4())
        res = self._base.upsert_by_id(self._test_collection_name, object_id, {'p': p})
        assert res
        ob = self._base.get_one(self._test_collection_name, {'_id': object_id})
        assert ob is not None
        assert ob['p'] == p

    def test_get_all(self):
        from core import Base
        object_id1 = str(uuid.uuid4())
        object_id2 = str(uuid.uuid4())
        object_id3 = str(uuid.uuid4())
        p1 = str(uuid.uuid4())
        p2 = str(uuid.uuid4())
        res = self._base.upsert_by_id(self._test_collection_name, object_id1, {'p': p1, 'a': 1})
        assert res
        res = self._base.upsert_by_id(self._test_collection_name, object_id2, {'p': p1, 'a': 2})
        assert res
        res = self._base.upsert_by_id(self._test_collection_name, object_id3, {'p': p2, 'a': 3})
        assert res
        aob = self._base.get_all(self._test_collection_name, {'p': p1})
        assert len(aob) == 2
        assert object_id1 in [ob['_id'] for ob in aob]
        assert object_id2 in [ob['_id'] for ob in aob]
        aob = self._base.get_all(self._test_collection_name, {'p': p1}, [('a', Base.asc)])
        assert len(aob) == 2
        assert aob[0]['_id'] == object_id1
        assert aob[1]['_id'] == object_id2
        aob = self._base.get_all(self._test_collection_name, {'p': p1}, [('a', Base.desc)])
        assert len(aob) == 2
        assert aob[0]['_id'] == object_id2
        assert aob[1]['_id'] == object_id1

    def test_insert(self):
        object_id = str(uuid.uuid4())
        #res = self._base.upsert_by_id(self._test_collection_name, object_id, {})
        res = self._base.insert(self._test_collection_name, {'object_id': object_id})
        aob = [ob for ob in self._test_collection.find({})]
        assert len(aob) == 1
        assert aob[0]['object_id'] == object_id

    def test_update(self):
        object_id1 = str(uuid.uuid4())
        object_id2 = str(uuid.uuid4())
        p1 = str(uuid.uuid4())
        p2 = str(uuid.uuid4())
        self._base.insert(self._test_collection_name, {'object_id': object_id1, 'p': p1})
        self._base.insert(self._test_collection_name, {'object_id': object_id2, 'p': p1})
        a = self._base.update(self._test_collection_name, {'object_id': object_id2}, {'p': p2})
        assert a
        aob = [ob for ob in self._test_collection.find({'p': p2})]
        assert len(aob) == 1
        assert aob[0]['object_id'] == object_id2
