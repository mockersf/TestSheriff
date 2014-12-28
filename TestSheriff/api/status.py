from flask import jsonify, request, url_for, abort
from flask.ext import restful
from flask.ext.restful import reqparse

from core.Status import Status as StatusCore
from core import Base

from .tools import add_link_or_expand, new_endpoint


def add_status(api, root='/api/', version='v1', path='statuses'):
    new_endpoint(api, 'statuses', "{0}{1}/{2}".format(root, version, path), List, can_expand=False)
    new_endpoint(api, 'status', "{0}{1}/{2}/<status_id>".format(root, version, path), Status, can_expand=True, function=status_get)


def prep_status(status):
    dict = status.to_dict()
    dict['_links'] = {}
    add_link_or_expand(dict, 'self', 'status', status_id=status._id)
    add_link_or_expand(dict, 'test', 'test', test_id=status._test_id)
    return dict


class List(restful.Resource):
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('test_id', type=str, help='test ID', required=False, location='args')
        parser.add_argument('status', type=str, help='status', required=False, location='args')
        parser.add_argument('type', type=str, help='test type', required=False, location='args')
        parser.add_argument('field', type=str, help='details field name', required=False, location='args')
        parser.add_argument('value', type=str, help='details field value', required=False, location='args')
        parser.add_argument('nb_status', type=int, help='number of status to return, by default 100', required=False, location='args', default=100)
        parser.add_argument('page', type=int, help='page to return', required=False, location='args', default=0)
        args = parser.parse_args()
        query_filter = {}
        if args['test_id'] is not None:
            query_filter[StatusCore._test_id] = args['test_id']
        if args['status'] is not None:
            query_filter[StatusCore._status] = args['status']
        if args['type'] is not None:
            query_filter[StatusCore._type] = args['type']
        if args['field'] is not None and args['value'] is not None:
            query_filter[StatusCore._details + '.' + args['field']] = args['value']
        statuses = StatusCore.list(query_filter=query_filter, sort=[(StatusCore._on, Base.desc)], page=args['page'], nb=args['nb_status'])
        statuses_preped = [prep_status(status) for status in statuses]
        return jsonify(result='Success', statuses=statuses_preped, count=len(statuses), total=statuses.count())
    def post(self):
        purge_result = None
        parser = reqparse.RequestParser()
        parser.add_argument('purge', help='Do we purge ?', required=False, location='args')
        args = parser.parse_args()
        purge = True
        if args['purge'] is not None:
            print('argparse : {0}'.format(args['purge']))
            if args['purge'].lower() == 'false':
                purge = False
            elif args['purge'].lower() == 'true':
                purge = True
            else:
                abort(400)
        data = request.get_json()
        status = StatusCore(test_id=data['test_id'], test_type=data['type'],
                            status=data['status'], details=data['details'])
        if purge:
            purge_result = status.purge()
        status.save_and_update()
        status = prep_status(status)
        return jsonify(result='Success', status=status, purge=purge_result)


def status_get(status_id):
    status = StatusCore(base_id=status_id).get()
    if status is None:
        abort(404)
    status = prep_status(status)
    return status


class Status(restful.Resource):
    def get(self, status_id):
        status = status_get(status_id)
        return jsonify(result='Success', status=status)
    def delete(self, status_id):
        status = StatusCore(base_id=status_id).remove()
        return jsonify(result='Success')
