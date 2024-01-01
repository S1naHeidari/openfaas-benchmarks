from numpy import matrix, linalg, random
from time import time
import json

def linpack(n):
    # LINPACK benchmarks
    ops = (2.0 * n) * n * n / 3.0 + (2.0 * n) * n

    # Create AxA array of random numbers -0.5 to 0.5
    A = random.random_sample((n, n)) - 0.5
    B = A.sum(axis=1)

    # Convert to matrices
    A = matrix(A)
    B = matrix(B.reshape((n, 1)))

    # Ax = B
    start = time()
    x = linalg.solve(A, B)
    latency = time() - start

    mflops = (ops * 1e-6 / latency)

    result = {
        'mflops': mflops,
        'latency': latency
    }

    return result

def handle(data):
    request_json = json.loads(data)

    number = int(request_json["number"])
    request_uuid = request_json['uuid']
    start_time = time()

    result = linpack(number)
    return {
        "statusCode": 200,
        "body": {
            **result,
            'start_time': start_time,
            'number': number,
            'uuid': request_uuid,
            'test_name': 'linpack'
        }
    }

#print(handle('{"number": 10, "uuid": "1234"}'))
