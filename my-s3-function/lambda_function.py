import json
import urllib.parse
import boto3
import logging
import requests
from requests.auth import HTTPBasicAuth
from requests_aws4auth import AWS4Auth
print('Loading function')
#hi

s3 = boto3.client('s3')
service = 'es'
credentials = boto3.Session().get_credentials()
region = 'us-east-1'
host = 'https://search-photos-pxscxjm3dnkxtaw7gkzgvmfe2y.us-east-1.es.amazonaws.com'
type = 'photos'
index = 'photo'
url = host + '/' + index + '/' + type
headers = {"Content-Type": "application/json"}

def lambda_handler(event, context):
    # print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    bucket_name, image_key, time = get_info(event)
    img_idx = {'S3Object': {'Bucket': bucket_name, 'Name': image_key}}

    img_json = make_json(bucket_name, image_key, time, get_label(img_idx))
    print(img_json)
    r = requests.post(url, auth=HTTPBasicAuth('Admin', 'Larry990217!'), json=img_json, headers=headers)
    print('Successfully uploaded to ES', r)
    # try:
    #     response = s3.get_object(Bucket=bucket, Key=key)
    #     print("CONTENT TYPE: " + response['ContentType'])
    #     return response['ContentType']
    # except Exception as e:
    #     print(e)
    #     print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
    #     raise e
        return {
        'statusCode': 200,
        'header':{
            
        }

    }


def get_info(event):
    record = event['Records'][-1]
    bucket_name = 'sp22-b2'
    # image_key = record['s3']['object']['key'].replace('+', ' ')
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    event_time = record['eventTime']
    return bucket_name, key, event_time


def get_label(img_idx):
    rekog_client = boto3.client('rekognition')
    rekog_response = rekog_client.detect_labels(Image=img_idx)
    print("get label finished")
    labels = rekog_response['Labels']
    print("+++++")
    print(labels)
    img_labels = []
    for label in labels:
        img_labels.append(label["Name"])
    return img_labels


def make_json(bucket_name, image_key, event_time, img_labels):
    json = {
        "objectKey": image_key,
        "bucket": bucket_name,
        "createdTimestamp": event_time,
        "labels": img_labels

    }
    return json
