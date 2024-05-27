from flask import Flask, request, jsonify
import gzip
import os
import uuid
from time import time

app = Flask(__name__)

TMP_DIR = "/tmp/files"
if not os.path.exists(TMP_DIR):
    os.makedirs(TMP_DIR)

def handle_compression(file_size, request_uuid):
    start_time = time()

    file_write_path = os.path.join(TMP_DIR, f'file-{str(uuid.uuid4())}')

    # Writing random data to the file
    start = time()
    with open(file_write_path, 'wb') as f:
        f.write(os.urandom(file_size * 1024 * 1024))
    disk_latency = time() - start

    # Compressing the file
    compressed_file_path = os.path.join(TMP_DIR, f'result-{str(uuid.uuid4())}.gz')
    with open(file_write_path, 'rb') as f:
        start = time()
        with gzip.open(compressed_file_path, 'wb') as gz:
            gz.writelines(f)
        compress_latency = time() - start

    return {
        "disk_latency": disk_latency,
        "compress_latency": compress_latency,
        "file_size": file_size,
        "start_time": start_time,
        "uuid": request_uuid,
        "test_name": "gzip-compression"
    }

@app.route('/compress-file', methods=['POST'])
def compress_file():
    data = request.json
    file_size = data['file_size']
    request_uuid = data['uuid']
    
    result = handle_compression(file_size, request_uuid)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)

