import boto3
import uuid
from time import time
import cv2
from botocore.client import Config
import json
import os

s3_client = boto3.client('s3', endpoint_url='http://192.168.56.11:30158',
                   aws_access_key_id='oC59DZmk0v0DLN318m2a',
                   aws_secret_access_key='3kzBqrXyMUzY4cat4J1CbZXgFqs7iRZUcVGyMyIa',
                   config=Config(signature_version='s3v4'))



tmp = "/tmp/vids/"
if not os.path.exists(tmp):
    os.makedirs(tmp)
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2


def video_processing(object_key, video_path):
    file_name = object_key.split(".")[FILE_NAME_INDEX]
    result_file_path = tmp+f'-output-{str(uuid.uuid4())}.avi'

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height))

    start = time()
    while video.isOpened():
        ret, frame = video.read()

        if ret:
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            tmp_file_path = tmp+'tmp.jpg'
            cv2.imwrite(tmp_file_path, gray_frame)
            gray_frame = cv2.imread(tmp_file_path)
            out.write(gray_frame)
        else:
            break

    latency = time() - start

    video.release()
    out.release()
    return latency, result_file_path


def handle(data):
    request_json = json.loads(data)

    #input_bucket = 'picturesinput'
    #object_key = 'input/input_sina.jpg'
    input_bucket = request_json["input_bucket"]
    object_key = request_json['object_key']
    output_bucket = request_json['output_bucket']
    request_uuid = request_json['uuid']
    start_time = time()

    download_path = tmp+ '/{}'.format(uuid.uuid4())
    #download_path = tmp+'{}{}'.format(uuid.uuid4(), object_key)

    s3_client.download_file(input_bucket, object_key, download_path)

    latency, upload_path = video_processing(object_key, download_path)

    s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_PATH_INDEX])

    return {
        "statusCode": 200,
        "body": {
            'latency': latency,
            'start_time': start_time,
            'uuid': request_uuid,
            'test_name': 'video-processing'
        }
    }

#print(handle('{"input_bucket": "vidsbucket", "object_key": "input/input.mp4", "output_bucket": "processedvids", "uuid": "1234"}'))
