import os
import pymongo
import datetime
from bson.objectid import ObjectId
from flask import Flask, jsonify, request, abort, g
import uuid


app = Flask(__name__)

time_format = '%Y-%m-%d %H:%M:%S'
base_prefix = ""

def base():
    connection = pymongo.MongoClient('localhost', 27017)
    base_status = connection[base_prefix + 'TestSheriff']#['status']
    return base_status

@app.route('/status/<test_id>', methods=['PUT', 'GET'])
def status(test_id):
    if request.method == 'PUT':
        return save_status(test_id)
    else:
        return get_status(test_id)

def save_status(test_id):
    transaction_id = str(uuid.uuid4())
    data = request.get_json()
    base_status = base()['status']
    base_test = base()['test']
    base_status.update({'test_id': test_id, 'last': 'true'},
                       {'$set': {'last': 'false', 'transaction_id': transaction_id}})
    now = datetime.datetime.now().strftime(time_format)
    status = {'test_id': test_id,
              'on': now,
              'status': data['status'],
              'details': data['details'],
              'type': data['type'],
              'comment': '',
              'last': 'true',
              'transaction_id': transaction_id,
             }
    result = base_status.insert(status)
    test = {'on': now, 'transaction_id': transaction_id, 'type': data['type']}
    a = base_test.update({'_id': test_id}, {'$set': test}, upsert=True)
    status['_id'] = str(status['_id'])
    return jsonify(result='Success', transaction_id=transaction_id, status=status)

def get_status(test_id):
    transaction_id = str(uuid.uuid4())
    base_status = base()['status']
    status = base_status.find_one({'test_id': test_id, 'last': 'true'})
    if status is None:
        test = base()['test'].find_one({'_id': test_id})
        if test is None:
            response = jsonify(result='Failure', transaction_id=transaction_id, message='No status found for id {0}'.format(test_id))
            response.status_code = 404
            return response
        else:
            status = {'test_id': test_id,
                      'on': test['on'],
                      'status': 'UNKNOWN',
                      'details': {},
                      'type': test['type'],
                      'comment': '',
                      'last': 'true',
                      'transaction_id': test['transaction_id'],
                      }
    if '_id' in status:
        status['_id'] = str(status['_id'])
    return jsonify(result='Success', transaction_id=transaction_id, status=status)
