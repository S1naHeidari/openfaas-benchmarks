from flask import Flask, request, jsonify
import threading
import boto3
import uuid
from time import time
import cv2
import os
from botocore.client import Config
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

TMP_VID = "/tmp/vids"
if not os.path.exists(TMP_VID):
    os.makedirs(TMP_VID)


def process_frame(frame):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

def video_processing(object_key, video_path):
    file_name = object_key.split("/")[-1]
    output_file_name = f'{str(uuid.uuid4())}.avi'

    result_file_path = os.path.join(TMP_VID, output_file_name)

    video = cv2.VideoCapture(video_path)

    width = int(video.get(3))
    height = int(video.get(4))

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, 20.0, (width, height), isColor=False)

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

    video.release()
    out.release()

    latency = time() - start

    return latency, result_file_path

def video_processing_task(data):
    input_bucket = data["input_bucket"]
    object_key = data['object_key']
    output_bucket = data['output_bucket']
    key_id = data['key_id']
    access_key = data['access_key']
    request_uuid = data['uuid']
    start_time = time()

    s3_client = boto3.client('s3', endpoint_url='http://192.168.56.1:9000',
                   aws_access_key_id=key_id,
                   aws_secret_access_key=access_key,
                   config=Config(signature_version='s3v4'))

    download_path = os.path.join(TMP_VID, f'{str(uuid.uuid4())}.mp4')
    s3_client.download_file(input_bucket, object_key, download_path)

    latency, upload_path = video_processing(object_key, download_path)

    upload_filename = upload_path.split("/")[-1]
    unique_filename = f'{str(uuid.uuid4())}-{upload_filename}'

    s3_client.upload_file(upload_path, output_bucket, unique_filename)

    return {
        "latency": latency,
        "start_time": start_time,
        "uuid": request_uuid,
        "test_name": "video-processing"
    }

def process_video_thread(data):
    result = video_processing_task(data)
    return result

@app.route('/process-video', methods=['POST'])
def process_video():
    data = request.json
    result = process_video_thread(data)
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)

