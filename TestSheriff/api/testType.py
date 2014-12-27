from flask import jsonify, url_for, abort, request
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Test import Test as TestCore
from core.Status import Status as StatusCore
from core.TestType import TestType as TestTypeCore
from core.Index import Index as IndexCore
from core import Base

from .tools import add_link_or_expand, new_endpoint


def add_test_type(api, root='/api/', version='v1', path='test_types'):
    new_endpoint(api, 'test_types', "{0}{1}/{2}".format(root, version, path), List, can_expand=False)
    new_endpoint(api, 'test_type', "{0}{1}/{2}/<test_type>".format(root, version, path), TestType, can_expand=True, function=testtype_get)
    new_endpoint(api, 'run', "{0}{1}/{2}/<test_type>/runs/<run_type>".format(root, version, path), Run, can_expand=True, function=run_get)
    new_endpoint(api, 'runs', "{0}{1}/{2}/<test_type>/runs".format(root, version, path), RunList, can_expand=True, function=runlist_get)
    new_endpoint(api, 'purge', "{0}{1}/{2}/<test_type>/purge".format(root, version, path), Purge, can_expand=True, function=purge_get)
    new_endpoint(api, 'test_type_indexes', "{0}{1}/{2}/<test_type>/indexes".format(root, version, path), IndexList, can_expand=False)
    new_endpoint(api, 'test_type_index', "{0}{1}/{2}/<test_type>/indexes/<field>".format(root, version, path), Index, can_expand=False)


def prep_test_type(test_type):
    tt_dict = test_type.to_dict()
    if 'run' in tt_dict:
        tt_dict.pop('run')
    if 'purge' in tt_dict:
        tt_dict.pop('purge')
    tt_dict['_links'] = {}
    add_link_or_expand(tt_dict, 'self', 'test_type', test_type=test_type._test_type)
    add_link_or_expand(tt_dict, 'tests', 'tests', test_type=test_type._test_type)
    add_link_or_expand(tt_dict, 'indexes', 'test_type_indexes', test_type=test_type._test_type)
    add_link_or_expand(tt_dict, 'run_types', 'runs', test_type=test_type._test_type)
    add_link_or_expand(tt_dict, 'purge', 'purge', test_type=test_type._test_type)
    return tt_dict


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
    def patch(self, test_type):
        testType = TestTypeCore(test_type=test_type).get_one()
        if testType is None:
            abort(404)
        parser = reqparse.RequestParser()
        parser.add_argument('doc_fields_to_index', type=str, help='list of the document fields to index', required=False, action='append')
        args = parser.parse_args()
        if args['doc_fields_to_index'] is not None:
            testType._doc_fields_to_index = args['doc_fields_to_index']
        testType.save()
        testType = prep_test_type(testType)
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


def run_get(test_type, run_type):
    testType = TestTypeCore(test_type=test_type).get_one()
    if testType is None:
        abort(404)
    run = testType.run(run_type)
    if run is None:
        abort(404)
    run_dict = {'_links': {}}
    run_dict['condition'] = run['condition'].to_dict()
    run_dict['modifier'] = run['modifier']
    add_link_or_expand(run_dict, 'self', 'run', test_type=test_type, run_type=run_type)
    return run_dict


def runlist_get(test_type):
    testType = TestTypeCore(test_type=test_type).get_one()
    if testType is None:
        abort(404)
    runs = [] if testType._run is None else [run for run in testType._run]
    runs.append('default')
    runs = {run: run_get(test_type, run) for run in runs}
    return runs


class RunList(restful.Resource):
    def get(self, test_type):
        runs = runlist_get(test_type)
        return jsonify(result='Success', runs=runs, count=len(runs))
    def post(self, test_type):
        data = request.get_json()
        run_type = data['run_type']
        modifier = data['modifier']
        condition = data['condition']
        testType = TestTypeCore(test_type=test_type).get_one()
        if testType is None:
            abort(404)
        if modifier not in TestTypeCore.modifiers:
            abort(400)
        if not testType.add_run_type(run_type, modifier, condition):
            abort(400)
        run = run_get(test_type, run_type)
        return jsonify(result='Success', run=run)


class Run(restful.Resource):
    def get(self, test_type, run_type):
        run = run_get(test_type, run_type)
        return jsonify(result='Success', run=run)


def purge_get(test_type):
    testType = TestTypeCore(test_type=test_type).get_one()
    if testType is None:
        abort(404)
    purge = testType.purge()
    purge_dict = {'_links': {}}
    purge_dict['condition'] = purge['condition'].to_dict()
    purge_dict['action'] = purge['action']
    add_link_or_expand(purge_dict, 'self', 'purge', test_type=test_type)
    return purge_dict


class Purge(restful.Resource):
    def get(self, test_type):
        purge = purge_get(test_type)
        return jsonify(result='Success', purge=purge)
    def post(self, test_type):
        data = request.get_json()
        action = data['action']
        condition = data['condition']
        testType = TestTypeCore(test_type=test_type).get_one()
        if testType is None:
            abort(404)
        if action not in TestTypeCore.actions:
            abort(400)
        if not testType.set_purge(action, condition):
            abort(400)
        purge = purge_get(test_type)
        return jsonify(result='Success', purge=purge)
