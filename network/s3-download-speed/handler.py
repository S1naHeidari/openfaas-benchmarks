import boto3
from time import time
import json
from botocore.client import Config
import uuid

s3_client = boto3.client('s3', endpoint_url='http://192.168.56.10:32390',
                   aws_access_key_id='hGuPvYhOD2vzVAGEC4Us',
                   aws_secret_access_key='mtUQrnx9O9wCjbNLBU68ul0TmTBJREncqQY8Kf2b',
                   config=Config(signature_version='s3v4'))

def handle(data):
    request_json = json.loads(data)

    #input_bucket = 'picturesinput'
    #object_key = 'input/input_sina.jpg'
    input_bucket = request_json["input_bucket"]
    object_key = request_json['object_key']
    output_bucket = request_json['output_bucket']
    request_uuid = request_json['uuid']
    start_time = time()

    #input_bucket = event.query['input_bucket']
    #object_key = event.query['object_key']
    #output_bucket = event.query['output_bucket']
    #start_time = float(event.query['start_time'])
    #request_uuid = event.query['uuid']

    new_name = str(uuid.uuid4())

    path = '/tmp/'+new_name

    start = time()
    s3_client.download_file(input_bucket, object_key, path)
    download_time = time() - start

    start = time()
    s3_client.upload_file(path, output_bucket, new_name)
    upload_time = time() - start

    return {
        "statusCode": 200,
        "body": {
            "download_time": download_time,
            "upload_time": upload_time,
            "start_time": start_time,
            "uuid": request_uuid,
            "test_name": "s3-download-speed"
            }
    }

#print(handle('{"input_bucket": "vidsbucket", "object_key": "input/v-3.mp4", "output_bucket": "downloadedvids", "uuid": "1234"}'))
