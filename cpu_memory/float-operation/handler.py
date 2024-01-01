import math
from time import time
import json

def float_operations(n):
    start = time()
    for i in range(0, n):
        sin_i = math.sin(i)
        cos_i = math.cos(i)
        sqrt_i = math.sqrt(i)
    latency = time() - start
    return latency

def handle(data):
    request_json = json.loads(data)

    number = int(request_json["number"])
    start_time = time()
    request_uuid = request_json["uuid"]

    latency = float_operations(number)

    return {
        "statusCode": 200,
        "body": {
            "latency": latency,
            "start_time": start_time,
            "uuid": request_uuid,
            "test_name": 'float-operation',
            "number": number
        }
    }
