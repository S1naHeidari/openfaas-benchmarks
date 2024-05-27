from flask import Flask, request, jsonify
import boto3
import uuid
from time import time
import cv2
import os
from botocore.client import Config

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
    if not video.isOpened():
        raise Exception("Error opening video file")

    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(result_file_path, fourcc, fps, (width, height), isColor=False)

    start = time()
    while True:
        ret, frame = video.read()
        if not ret:
            break
        gray_frame = process_frame(frame)
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


    download_path = os.path.join(TMP_VID, f'{str(uuid.uuid4())}.avi')
    try:
        s3_client.download_file(input_bucket, object_key, download_path)
    except Exception as e:
        return {"error": f"Failed to download file: {str(e)}"}, 500

    try:
        latency, upload_path = video_processing(object_key, download_path)
    except Exception as e:
        return {"error": f"Video processing failed: {str(e)}"}, 500

    upload_filename = upload_path.split("/")[-1]
    unique_filename = f'{str(uuid.uuid4())}-{upload_filename}'
    try:
        s3_client.upload_file(upload_path, output_bucket, unique_filename)
    except Exception as e:
        return {"error": f"Failed to upload file: {str(e)}"}, 500

    return {
        "latency": latency,
        "start_time": start_time,
        "uuid": request_uuid,
        "test_name": "video-processing"
    }, 200

@app.route('/process-video', methods=['POST'])
def process_video():
    data = request.json
    result, status_code = video_processing_task(data)
    return jsonify(result), status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234)

