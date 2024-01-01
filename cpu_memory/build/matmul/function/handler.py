import numpy as np
from time import time
import json

def matmul(n):
    A = np.random.rand(n, n)
    B = np.random.rand(n, n)

    start = time()
    C = np.matmul(A, B)
    latency = time() - start
    return latency

def handle(data):
    request_json = json.loads(data)

    number = int(request_json["number"])
    start_time = time()
    request_uuid = request_json["uuid"]

    latency = matmul(number)
    return {
        "statusCode": 200,
        "body": {
            'latency': latency,
            'start_time': start_time,
            'uuid': request_uuid,
            'number': number,
            'test_name': 'matmul'
        }
    }
#print(handle('{"number":10, "uuid":"1234"}'))
