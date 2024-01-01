import boto3
import uuid
from time import time
from PIL import Image
from botocore.client import Config
from PIL import Image, ImageFilter
import json
import os

s3_client = boto3.client('s3', endpoint_url='http://192.168.56.11:30158',
                   aws_access_key_id='H0eiqZBEeNxfo4A8xOfM',
                   aws_secret_access_key='QcZkFH8u4jSjKZleAoXPsO0ngReCnOwTntQTkxJ2',
                   config=Config(signature_version='s3v4'))


FILE_NAME_INDEX = 2
TMP = "/tmp/pics"
if not os.path.exists(TMP):
    os.makedirs(TMP)


def flip(image, file_name):
    path_list = []
    name = file_name.split('/')[1]
    #print(name)
    path = TMP + "flip-left-right-"+str(uuid.uuid4()) + name
    img = image.transpose(Image.FLIP_LEFT_RIGHT)
    img.save(path)
    path_list.append(path)

    path = TMP + "flip-top-bottom-" +str(uuid.uuid4())+ name
    img = image.transpose(Image.FLIP_TOP_BOTTOM)
    img.save(path)
    path_list.append(path)

    return path_list


def rotate(image, file_name):
    path_list = []
    name = file_name.split('/')[1]
    path = TMP + "rotate-90-" +str(uuid.uuid4())+ name
    img = image.transpose(Image.ROTATE_90)
    img.save(path)
    path_list.append(path)

    path = TMP + "rotate-180-" +str(uuid.uuid4())+ name
    img = image.transpose(Image.ROTATE_180)
    img.save(path)
    path_list.append(path)

    path = TMP + "rotate-270-"+str(uuid.uuid4()) + name
    img = image.transpose(Image.ROTATE_270)
    img.save(path)
    path_list.append(path)

    return path_list


def filter(image, file_name):
    path_list = []
    name = file_name.split('/')[1]
    path = TMP + "blur-" +str(uuid.uuid4()) + name
    img = image.filter(ImageFilter.BLUR)
    img.save(path)
    path_list.append(path)

    path = TMP + "contour-" +str(uuid.uuid4()) + name
    img = image.filter(ImageFilter.CONTOUR)
    img.save(path)
    path_list.append(path)

    path = TMP + "sharpen-" +str(uuid.uuid4()) + name
    img = image.filter(ImageFilter.SHARPEN)
    img.save(path)
    path_list.append(path)

    return path_list


def gray_scale(image, file_name):
    name = file_name.split('/')[1]
    path = TMP + "gray-scale-" +str(uuid.uuid4()) + name
    img = image.convert('L')
    img.save(path)
    return [path]


def resize(image, file_name):
    name = file_name.split('/')[1]
    path = TMP + "resized-" +str(uuid.uuid4()) + name
    image.thumbnail((128, 128))
    image.save(path)
    return [path]


def image_processing(file_name, image_path):
    path_list = []
    start = time()
    with Image.open(image_path) as image:
        tmp = image
        path_list += flip(image, file_name)
        path_list += rotate(image, file_name)
        path_list += filter(image, file_name)
        path_list += gray_scale(image, file_name)
        path_list += resize(image, file_name)

    latency = time() - start
    return latency, path_list


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
    download_path = '/tmp/pics/{}.jpg'.format(uuid.uuid4())
    #download_path = '/tmp/{}'.format(uuid.uuid4())
    # if not os.path.exists(download_path):
    #     os.makedirs(download_path)

    s3_client.download_file(input_bucket, object_key, download_path)

    latency, path_list = image_processing(object_key, download_path)

    for upload_path in path_list:
        s3_client.upload_file(upload_path, output_bucket, upload_path.split("/")[FILE_NAME_INDEX])

    return {
        "statusCode": 200,
        "body": {
            'latency': latency,
            'start_time': start_time,
            'uuid': request_uuid,
            'test_name': 'image-processing'
        }
    }


#print(handle('{"input_bucket": "picturesinput", "object_key": "input/input_sina.jpg", "output_bucket": "processedimages", "uuid": "1234"}'))
