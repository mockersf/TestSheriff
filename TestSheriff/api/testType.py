from flask import jsonify, url_for, abort
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Test import Test as TestCore
from core.Status import Status as StatusCore
from core.TestType import TestType as TestTypeCore
from core.Index import Index as IndexCore
from core import Base

from .tools import add_link_or_expand, new_endpoint


def add_test_type(api, version='v1', path='test_types'):
    new_endpoint(api, 'test_types', "/{0}/{1}".format(version, path), List, can_expand=False)
    new_endpoint(api, 'test_type', "/{0}/{1}/<test_type>".format(version, path), TestType, can_expand=True, function=testtype_get)
    new_endpoint(api, 'test_type_indexes', "/{0}/{1}/<test_type>/indexes".format(version, path), IndexList, can_expand=False)
    new_endpoint(api, 'test_type_index', "/{0}/{1}/<test_type>/indexes/<field>".format(version, path), Index, can_expand=False)


def prep_test_type(test_type):
    dict = test_type.to_dict()
    dict['_links'] = {}
    add_link_or_expand(dict, 'self', 'test_type', test_type=test_type._test_type)
    add_link_or_expand(dict, 'tests', 'tests', test_type=test_type._test_type)
    return dict


class List(restful.Resource):
    def get(self):
        test_types = TestTypeCore().get_all()
        test_types = [prep_test_type(test_type) for test_type in test_types]
        return jsonify(result='Success', test_types=test_types, count=len(test_types))


def testtype_get(test_type):
    testType = TestTypeCore(test_type=test_type).get_one()
    if testType is None:
        abort(404)
    testType = prep_test_type(testType)
    return testType


class TestType(restful.Resource):
    def get(self, test_type):
        testType = testtype_get(test_type)
        return jsonify(result='Success', test_type=testType)


def prep_index(index):
    index_dict = index.to_dict()
    index_dict['_links'] = {}
    add_link_or_expand(index_dict, 'self', 'test_type_index', test_type=index._test_type, field=index._field)
    add_link_or_expand(index_dict, 'test_type', 'test_type', test_type=index._test_type)
    return index_dict


class IndexList(restful.Resource):
    def get(self, test_type):
        testType = TestTypeCore(test_type=test_type).get_one()
        if testType is None:
            abort(404)
        indexes = IndexCore(test_type=test_type).get_all()
        indexes = [prep_index(index) for index in indexes]
        return jsonify(result='Success', indexes=indexes, count=len(indexes))


class Index(restful.Resource):
    def get(self, test_type, field):
        testType = TestTypeCore(test_type=test_type).get_one()
        if testType is None:
            abort(404)
        index = IndexCore(test_type=test_type, field=field).get()
        if index is None:
            abort(404)
        index = prep_index(index)
        return jsonify(result='Success', index=index)
