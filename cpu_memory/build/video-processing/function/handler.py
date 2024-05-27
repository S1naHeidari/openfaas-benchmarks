import boto3
import uuid
from time import time
import cv2
from botocore.client import Config
import json
import os
from concurrent.futures import ThreadPoolExecutor

s3_client = boto3.client('s3', endpoint_url='http://192.168.56.10:32390',
                   aws_access_key_id='hGuPvYhOD2vzVAGEC4Us',
                   aws_secret_access_key='mtUQrnx9O9wCjbNLBU68ul0TmTBJREncqQY8Kf2b',
                   config=Config(signature_version='s3v4'))

tmp = "/tmp/vids/"
if not os.path.exists(tmp):
    os.makedirs(tmp)
FILE_NAME_INDEX = 0
FILE_PATH_INDEX = 2

def process_frame(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def video_processing(object_key, video_path):
    file_name = object_key.split(".")[FILE_NAME_INDEX]
    output_file_name = f'{str(uuid.uuid4())}.avi'  # Unique output filename using UUID

    result_file_path = os.path.join(tmp, output_file_name)

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height), isColor=False)  # Specify isColor=False for grayscale output

    start = time()
    with ThreadPoolExecutor() as executor:
        futures = []
        while video.isOpened():
            ret, frame = video.read()
            if ret:
                futures.append(executor.submit(process_frame, frame))
            else:
                break
        for future in futures:
            gray_frame = future.result()
            out.write(gray_frame)
    
    # Release the video capture and writer objects
    video.release()
    out.release()
    
    latency = time() - start

    return latency, result_file_path

def handle(data):
    request_json = json.loads(data)
    input_bucket = request_json["input_bucket"]
    object_key = request_json['object_key']
    output_bucket = request_json['output_bucket']
    request_uuid = request_json['uuid']
    start_time = time()

    download_path = os.path.join(tmp, str(uuid.uuid4()))
    s3_client.download_file(input_bucket, object_key, download_path)

    latency, upload_path = video_processing(object_key, download_path)

    upload_filename = upload_path.split("/")[-1]  # Extract filename from the path
    unique_filename = f'{str(uuid.uuid4())}-{upload_filename}'  # Add UUID prefix to the filename

    s3_client.upload_file(upload_path, output_bucket, unique_filename)  # Upload with the unique filename

    return {
        "statusCode": 200,
        "body": {
            'latency': latency,
            'start_time': start_time,
            'uuid': request_uuid,
            'test_name': 'video-processing'
        }
    }

#print(handle('{"input_bucket": "vidsbucket", "object_key": "input/v-1.mp4", "output_bucket": "processedvids", "uuid": "1234"}'))
