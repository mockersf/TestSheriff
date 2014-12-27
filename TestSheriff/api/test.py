from flask import jsonify, url_for, abort
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Test import Test as TestCore
from core.Status import Status as StatusCore
from core import Base

from .tools import add_link_or_expand, new_endpoint


def add_test(api, root='/api/', version='v1', path='tests'):
    "{0}{1}/{2}".format(root, version, path)
    new_endpoint(api, 'tests', "{0}{1}/{2}".format(root, version, path), List, can_expand=True, function=list_get)
    new_endpoint(api, 'test', "{0}{1}/{2}/<test_id>".format(root, version, path), Test, can_expand=True, function=test_get)
    new_endpoint(api, 'test_run', "{0}{1}/{2}/<test_id>/run".format(root, version, path), Run, can_expand=True, function=run_get)
    new_endpoint(api, 'test_purge', "{0}{1}/{2}/<test_id>/purge".format(root, version, path), Purge, can_expand=False)
    new_endpoint(api, 'test_run_type', "{0}{1}/{2}/<test_id>/run/<run_type>".format(root, version, path), RunType, can_expand=True, function=run_get)


def prep_test(test, statuses={}):
    test_dict = test.to_dict()
    test_dict['_links'] = {}
    add_link_or_expand(test_dict, 'self', 'test', test_id=test._test_id)
    add_link_or_expand(test_dict, 'statuses', 'statuses', test_id=test._test_id)
    add_link_or_expand(test_dict, 'test_type', 'test_type', test_type=test._type)
    add_link_or_expand(test_dict, 'run', 'test_run', test_id=test._test_id)
    for status in statuses:
        add_link_or_expand(test_dict, status, 'status', status_id=statuses[status]._id)
    return test_dict


def list_get(test_type=None):
    query_filter = {}
    if test_type is not None:
        query_filter = {TestCore._type: test_type}
    tests = TestCore().get_all(additional_filter=query_filter)#(sort=[(StatusCore._on, Base.desc)])
    tests = [prep_test(test) for test in tests]
    return tests


class List(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('test_type', type=str, help='test type', required=False, location='args')
        args = parser.parse_args()
        tests = list_get(args['test_type'])
        return jsonify(result='Success', tests=tests, count=len(tests))
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('test_id', type=str, help='test ID', required=True, location='json')
        parser.add_argument('type', type=str, help='test type', required=True, location='json')
        parser.add_argument('owner', type=str, help='test owner', required=False, location='json')
        args = parser.parse_args()
        test = TestCore(test_id=args['test_id'], test_type=args['type'], owner=args['owner'])
        test.save()
        test = prep_test(test)
        return jsonify(result='Success', test=test)


def test_get(test_id):
    test = TestCore(test_id=test_id).get_one()
    if test is None:
        abort(404)
    statuses = {}
    lastStatuses = StatusCore.list(query_filter={StatusCore._test_id: test._test_id,
                                                 StatusCore._last: True},
                                   sort=[(StatusCore._on, Base.desc)])
    if lastStatuses != []:
        statuses['last_status'] = lastStatuses[0]
    lastSuccess = StatusCore.list(query_filter={StatusCore._test_id: test._test_id,
                                                StatusCore._status: 'SUCCESS'},
                                  sort=[(StatusCore._on, Base.desc)])
    if lastSuccess != []:
        statuses['last_status_success'] = lastSuccess[0]
    lastFailure = StatusCore.list(query_filter={StatusCore._test_id: test._test_id,
                                                StatusCore._status: 'FAILURE'},
                                  sort=[(StatusCore._on, Base.desc)])
    if lastFailure != []:
        statuses['last_status_failure'] = lastFailure[0]
    test = prep_test(test, statuses)
    return test


class Test(restful.Resource):
    def get(self, test_id):
        test = test_get(test_id)
        return jsonify(result='Success', test=test)


def run_get(test_id, run_type):
    status = StatusCore(test_id=test_id)
    status.add_unknown_if_none_exist()
    run = status.should_i_run(run_type)
    if run is None:
        abort(404)
    return run


class Run(restful.Resource):
    def get(self, test_id):
        run = run_get(test_id, 'default')
        return jsonify(result='Success', run=run)


class RunType(restful.Resource):
    def get(self, test_id, run_type):
        run = run_get(test_id, run_type)
        return jsonify(result='Success', run=run)


class Purge(restful.Resource):
    def get(self, test_id):
        status = StatusCore(test_id=test_id)
        status.add_unknown_if_none_exist()
        result = status.purge()
        return jsonify(result='Success', purge=result)
