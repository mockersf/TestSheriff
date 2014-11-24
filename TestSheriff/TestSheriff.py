from flask import Flask, jsonify, request

from core.Test import Test
from core.Status import Status


app = Flask(__name__)


@app.route('/status/<test_id>', methods=['PUT', 'GET'])
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
