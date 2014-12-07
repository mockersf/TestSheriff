from flask import jsonify, request, url_for, abort
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Status import Status as StatusCore
from core import Base

from .tools import build_url_other


def add_status(api, version='v1', path='statuses'):
    api.add_resource(List, "/{0}/{1}".format(version, path), endpoint='statuses')
    api.add_resource(Status, "/{0}/{1}/<status_id>".format(version, path), endpoint='status')


def prep_status(status):
    dict = status.to_dict()
    dict['_links'] = {}
    dict['_links']['self'] = {'href': url_for('status', status_id=status._id)}
    dict['_links']['test'] = {'href': build_url_other('test', test_id=status._test_id)}
    return dict


class List(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('test_id', type=str, help='test ID', required=False, location='args')
        args = parser.parse_args()
        query_filter = {}
        if args['test_id'] is not None:
            query_filter = {StatusCore._test_id: args['test_id']}
        statuses = StatusCore.list(query_filter=query_filter, sort=[(StatusCore._on, Base.desc)])
        statuses = [prep_status(status) for status in statuses]
        return jsonify(result='Success', statuses=statuses, count=len(statuses))
    def post(self):
        data = request.get_json()
        status = StatusCore(test_id=data['test_id'], test_type=data['type'],
                            status=data['status'], details=data['details'])
        status.save_and_update()
        status = prep_status(status)
        return jsonify(result='Success', status=status)


class Status(restful.Resource):
    def get(self, status_id):
        status = StatusCore(base_id=status_id).get()
        if status is None:
            abort(404)
        status = prep_status(status)
        return jsonify(result='Success', status=status)
