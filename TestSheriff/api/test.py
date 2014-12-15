from flask import jsonify, url_for, abort
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Test import Test as TestCore
from core.Status import Status as StatusCore
from core import Base

from .tools import build_url_other


def add_test(api, version='v1', path='tests'):
    api.add_resource(List, "/{0}/{1}".format(version, path), endpoint='tests')
    api.add_resource(Test, "/{0}/{1}/<test_id>".format(version, path), endpoint='test')



def prep_test(test, statuses={}):
    dict = test.to_dict()
    dict['_links'] = {}
    dict['_links']['self'] = {'href': url_for('test', test_id=test._test_id)}
    dict['_links']['statuses'] = {'href': build_url_other('statuses', test_id=test._test_id)}
    for status in statuses:
        dict['_links'][status] = {'href': build_url_other('status', status_id=statuses[status]._id)}
    return dict


class List(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('test_type', type=str, help='test type', required=False, location='args')
        args = parser.parse_args()
        query_filter = {}
        if args['test_type'] is not None:
            query_filter = {TestCore._type: args['test_type']}
        tests = TestCore().get_all(additional_filter=query_filter)#(sort=[(StatusCore._on, Base.desc)])
        tests = [prep_test(test) for test in tests]
        return jsonify(result='Success', tests=tests)
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


class Test(restful.Resource):
    def get(self, test_id):
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
        return jsonify(result='Success', test=test)
