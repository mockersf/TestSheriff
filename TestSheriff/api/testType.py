from flask import jsonify, url_for, abort
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Test import Test as TestCore
from core.Status import Status as StatusCore
from core.TestType import TestType as TestTypeCore
from core import Base

from .tools import add_link_or_expand, new_endpoint


def add_test_type(api, version='v1', path='test_types'):
    new_endpoint(api, 'test_types', "/{0}/{1}".format(version, path), List, can_expand=False)
    new_endpoint(api, 'test_type', "/{0}/{1}/<test_type>".format(version, path), TestType, can_expand=True, function=testtype_get)


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
        return jsonify(result='Success', test_types=test_types)


def testtype_get(test_type):
    testType = TestTypeCore(test_type=test_type).get_one()
    if testType is None:
        abort(404)
    testType = prep_test_type(testType)
    return testType

class TestType(restful.Resource):
    def get(self, test_type):
        testType = test_get(test_type)
        if testType is None:
            abort(404)
        testType = prep_test_type(testType)
        return jsonify(result='Success', test_type=testType)


class IndexList(restful.Resource):
    def get(self, test_type):
        testType = TestTypeCore(test_type=test_type).get_one()
        if testType is None:
            abort(404)
