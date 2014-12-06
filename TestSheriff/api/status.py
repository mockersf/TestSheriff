from flask import jsonify, request, url_for, Blueprint, abort

from TestSheriff_flask import app

from core.Test import Test
from core.Status import Status
from core import Base


status_bp = Blueprint('status_v1', __name__)

def prep_status(status):
    dict = status.to_dict()
    dict['_links'] = {'self': {'href': url_for('status_v1.details', status_id=status._id)}}
    return dict


@status_bp.route('/', methods=['GET', 'POST'])
def list():
    if request.method == 'GET':
        statuses = Status.list(sort=[(Status._on, Base.desc)])
        statuses = [prep_status(status) for status in statuses]
        return jsonify(result='Success', statuses=statuses)
    if request.method == 'POST':
        data = request.get_json()
        status = Status(test_id=data['test_id'], test_type=data['type'],
                        status=data['status'], details=data['details'])
        status.save_and_update()
        status = prep_status(status)
        return jsonify(result='Success', status=status)


@status_bp.route('/<status_id>', methods=['GET'])
def details(status_id):
    status = Status(base_id=status_id).get()
    if status is None:
        abort(404)
    status = prep_status(status)
    return jsonify(result='Success', status=status)


@app.route('/status/<test_id>', methods=['PUT', 'POST', 'GET'])
def status(test_id):
    if request.method == 'PUT':
        return save_status(test_id)
    else:
        return get_status(test_id)


def save_status(test_id):
    data = request.get_json()
    status = Status(test_id=test_id, test_type=data['type'],
                    status=data['status'], details=data['details'])
    status.save_and_update()
    return jsonify(result='Success', status=status.to_dict())


def get_status(test_id):
    status = Status(test_id=test_id).get_last()
    if status is None:
        current_test = Test(test_id=test_id)
        test = current_test.get_one()
        status = Status(test_id=test_id, on=test._last_seen, status='UNKNOWN',
                        details={}, test_type=test._type, last=True)
    return jsonify(result='Success', status=status.to_dict())
