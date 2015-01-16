from . import Base


class CoreObject(object):
    collection = 'no_collection'

    def __init__(self):
        pass

    @classmethod
    def get_all(cls, query_filter=None, sort=None, page=None, nb_item=None):
        if query_filter is None:
            query_filter = {}
        cursor = Base.Base().get_all(cls.collection, query_filter, sort, page, nb_item)
        cursor._transform = lambda bt: cls.from_dict(bt) # pylint: disable=unnecessary-lambda
        return cursor

    @classmethod
    def get_one(cls, query_filter):
        res = Base.Base().get_one(cls.collection, query_filter)
        return cls.from_dict(res) if res is not None else None

    def save_by_id(self, object_id):
        return Base.Base().upsert_by_id(self.collection, object_id, self.to_dict())

    def to_dict(self):
        dict_of_self = {}
        for attribute in dir(self.__class__):
            if attribute not in ['collection', '__module__']:
                if type(getattr(self.__class__, attribute)) == str:
                    if getattr(self, attribute) is not None:
                        dict_of_self[getattr(self.__class__, attribute)] = getattr(self, attribute)
        return dict_of_self

    @classmethod
    def from_dict(cls, object_dict):
        new_object = cls()
        for attribute in dir(cls):
            if attribute not in ['collection', '__module__']:
                if type(getattr(cls, attribute)) == str:
                    if getattr(cls, attribute) in object_dict:
                        setattr(new_object, attribute, object_dict[getattr(cls, attribute)])
        return new_object
