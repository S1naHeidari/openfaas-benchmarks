from flask import Flask, request, jsonify
import subprocess
import uuid
import json
from time import time
import os

app = Flask(__name__)

TMP_DIR = "/tmp"
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

def handle_io_operation(bs, count, request_uuid):
    start_time = time()
    identifier = str(uuid.uuid4())
    file_path = os.path.join(TMP_DIR, f'out-{identifier}')
    log_path = os.path.join(TMP_DIR, f'io_write_logs-{identifier}')

    with open(log_path, 'w') as out_fd:
        dd = subprocess.Popen(['dd', 'if=/dev/zero', f'of={file_path}', f'bs={bs}', f'count={count}', 'oflag=dsync'], stderr=out_fd)
        dd.communicate()

    result = ""
    with open(log_path, 'r') as logs:
        result = str(logs.readlines()[2]).replace('\n', '')

    latency = time() - start_time

    return {
        "latency": latency,
        "message": result,
        "start_time": start_time,
        "uuid": request_uuid,
        "test_name": "dd",
        "bs": bs,
        "count": count
    }

@app.route('/io-operation', methods=['POST'])
def io_operation():
    data = request.json
    bs = data['bs']
    count = data['count']
    request_uuid = data['uuid']
    
    result = handle_io_operation(bs, count, request_uuid)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)

