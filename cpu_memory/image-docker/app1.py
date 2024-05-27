from flask import Flask, request, jsonify
import threading
import boto3
import uuid
from time import time
from PIL import Image
import os
from botocore.client import Config

app = Flask(__name__)

TMP = "/tmp/pics"
if not os.path.exists(TMP):
    os.makedirs(TMP)

FILE_NAME_INDEX = 2

def resize(image, file_name):
    name = file_name.split('/')[1]
    path = os.path.join(TMP, "resized-" + str(uuid.uuid4()) + name)
    image.thumbnail((128, 128))
    image.save(path)
    return [path]

def image_processing(file_name, image_path):
    path_list = []
    with Image.open(image_path) as image:
        path_list += resize(image, file_name)
    return path_list

def image_processing_task(data):
    request_json = data
    input_bucket = request_json["input_bucket"]
    object_key = request_json['object_key']
    output_bucket = request_json['output_bucket']
    key_id = request_json['key_id']
    access_key = request_json['access_key']
    request_uuid = request_json['uuid']
    start_time = time()

    s3_client = boto3.client('s3', endpoint_url='http://192.168.56.1:9000',
                   aws_access_key_id=key_id,
                   aws_secret_access_key=access_key,
                   config=Config(signature_version='s3v4'))

    download_path = os.path.join(TMP, '{}.jpg'.format(uuid.uuid4()))
    s3_client.download_file(input_bucket, object_key, download_path)

    path_list = image_processing(object_key, download_path)

    # for upload_path in path_list:
    #     s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_NAME_INDEX])
    latency = time() - start_time

    return {
        "latency": latency,
        "start_time": start_time,
        "uuid": request_uuid,
        "test_name": "image-processing"
    }

def process_image_thread(data):
    result = image_processing_task(data)
    return result

@app.route('/process-image', methods=['POST'])
def process_image():
    data = request.json
    result = process_image_thread(data)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run()

