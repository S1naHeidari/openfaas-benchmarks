import json
from urllib.request import urlopen
from time import time
import json

def handle(data):
    request_json = json.loads(data)

    link = request_json["link"]
    request_uuid = request_json['uuid']
    start_time = time()

    #link = event.query['link']
    #start_time = float(event.query['start_time'])
    #request_uuid = event.query['uuid']

    start = time()
    f = urlopen(link)
    data = f.read().decode("utf-8")
    network = time() - start

    start = time()
    json_data = json.loads(data)
    str_json = json.dumps(json_data, indent=4)
    latency = time() - start

    return {
        "statusCode": 200,
        "body": {
            'latency': latency,
            'start_time': start_time,
            'uuid': request_uuid,
            'test_name': 'json-dumps-loads'
        }
    }

#print(handle('{"link": "http://api.worldbank.org/v2/countries/USA/indicators/NY.GDP.MKTP.CD?per_page=5000&format=json", "uuid": "1234"}'))
