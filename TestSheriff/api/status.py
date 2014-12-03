from flask import jsonify, request

from TestSheriff_flask import app

from core.Test import Test
from core.Status import Status
from core import Base

@app.route('/status', methods=['GET'])
def list_status():
    statuses = Status.list(sort=[('on', Base.desc)])
    return jsonify(result='Success', statuses=[status.to_dict() for status in statuses])

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
