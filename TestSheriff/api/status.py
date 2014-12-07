from flask import jsonify, request, url_for, abort
from flask.ext import restful
from werkzeug.routing import BuildError

from core.Status import Status as StatusCore
from core import Base


def add_status(api, version='v1', path='statuses'):
    api.add_resource(List, "/{0}/{1}".format(version, path), endpoint='statuses')
    api.add_resource(Status, "/{0}/{1}/<status_id>".format(version, path), endpoint='status')


def prep_status(status):
    dict = status.to_dict()
    dict['_links'] = {}
    dict['_links']['self'] = {'href': url_for('status', status_id=status._id)}
    try:
        dict['_links']['test'] = {'href': url_for('test', test_id=status._test_id)}
    except BuildError:
        pass
    return dict


class List(restful.Resource):
    def get(self):
        statuses = StatusCore.list(sort=[(StatusCore._on, Base.desc)])
        statuses = [prep_status(status) for status in statuses]
        return jsonify(result='Success', statuses=statuses)
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
