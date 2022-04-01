import json
import boto3
import os
import logging
import requests
import json
import logging
import uuid
from requests.auth import HTTPBasicAuth
from requests_aws4auth import AWS4Auth

logger = logging.getLogger()

logger.setLevel(logging.DEBUG)

""" --- Functions that control the bot's behavior --- """

#hi
def lambda_handler(event, context):
    print("ppppppp")
    print(event)
    print("oooooooo")
    text = event['queryStringParameters']['q'] #get text input from lex
    print("+++")
    # event["currentIntent"]
    response = get_labels(text)
    print(response)
    result=es_service(response, event)
    temp = find_s3_path(result)
    # return {
    #     "dialogAction": {
    #         "type": "Close",
    #         "fulfillmentState": "Fulfilled",
    #         "message": {
    #             'contentType': 'PlainText',
    #             'content':"Yes"
    #         }
    #     }
    # }
    # return {
    #     'statusCode':200,
    #     'body': json.dumps(temp),
    #     "headers": {"Access-Control-Allow-Origin":"*","Content-Type":"application/json"},
    #     "isBase64Encoded": False
    # }
    
    return {
        'statusCode':200,
    'body':json.dumps( {
            'imagePaths':temp,
            'userQuery':event,
            'labels': response,
        }),
        "headers": {"Access-Control-Allow-Origin":"*","Content-Type":"application/json"},
        }



def es_service(response, event):
    service = 'es'
    region = 'us-east-1'
    response_slots = response['slots']
    host = 'https://search-photos-pxscxjm3dnkxtaw7gkzgvmfe2y.us-east-1.es.amazonaws.com'
    type = 'photos'
    index = 'photo'
    url = host + '/' + index + '/' + '_search'
    headers = {"Content-Type": "application/json"}
    region = 'us-east-1'
    print(response)
    result = []
    word_list = list()
    # response_slots = event["currentIntent"]["slots"]  # gives labels from lex
    for key, value in response_slots.items():
        if value:
            word_list.append(value)
        # word_list = set(word_list)  # INPUT VAR for ES
        # logger.info("word_list:{}".format(word_list))
        # print(word_list)
    for word in word_list:
        query = {
            "size": 3,
            "query": {
                "multi_match": {
                    "query": word,
                    "fields": ["labels"]
                }
            }
        }
        r = requests.get(url, auth=HTTPBasicAuth('Admin', 'Larry990217!'), data=json.dumps(query),
                         headers=headers).json()
        print("+++++")
        print(r)
        logger.info("r:{}".format(r))
        result.append(r['hits']['hits'])
    print("1111111")
    print(result)
    print("1111111")
    # logger.info("result form elasticsearch:{}".format(result))
    return result


def find_s3_path(result):
    res = {}
    for each_res in result:
        each_res = each_res[0]
        res[each_res['_source']['objectKey'].split('/')[-1]] = 'https://' + each_res['_source'][
            'bucket'] + '.s3.amazonaws.com/' + each_res['_source']['objectKey'].replace(' ', "+")

    logger.info("res:{}".format(res))
    print("-----")
    print(res)
    return res


# logger = logging.getLogger()
# logger.setLevel(logging.INFO)
# from botocore.vendored import requests

# service = 'es'
# region = 'us-east-1'
# host = 'https://search-photos-pxscxjm3dnkxtaw7gkzgvmfe2y.us-east-1.es.amazonaws.com'
# type = 'photos'
# index = 'photo'
# url = host + '/' + index + '/' + type
# headers = {"Content-Type": "application/json"}
# region = 'us-east-1'
# lex = boto3.client('lex-runtime', region_name=region)

# def lambda_handler(event, context):
#     logger.info("event:{}".format(event))
#     print(event)
#     text = event['queryStringParameters']['q']  # get text input from lex
#     print(text)

#     # logger.info("raw text:{}".format(text))
#     # if text in ["give me use_voice"]:
#     #     logger.info("using voice!!!!!!!!!!!!!!!!!!!!11")
#     #     # text = use_voice()
#     #     text="tiger"
#     # logger.info("text:{}".format(text))

#     # client = boto3.client('lex-runtime')
#     # response=get_labels(text)
#     # print(response)
#     # logger.info("response:{}".format(response))
#     # response_slots = response['slots']  # gives labels from lex

#     # logger.info("slots:{}".format(response_slots))
#     # word_list = list()
#     # for key, value in response_slots.items():
#     #     if value:
#     #         word_list.append(value)
#     # word_list = set(word_list)  # INPUT VAR for ES
#     # logger.info("word_list:{}".format(word_list))

#     # for word in word_list:
#     #     query = {
#     #         "size": 5,
#     #         "query": {
#     #             "multi_match": {
#     #                 "query": word,
#     #                 "fields": ["labels"]
#     #             }
#     #         }
#     #     }
#     # r = requests.get(url, auth=HTTPBasicAuth('Admin', 'Larry990217!'), data=json.dumps(query), headers=headers).json()
#     # logger.info("r:{}".format(r))
#     # result = r['hits']['hits']
#     # logger.info("result form elasticsearch:{}".format(result))
#     # res = {}
#     # for each_res in result:
#     #     res[each_res['_source']['objectKey'].split('/')[-1]] = 'https://' + each_res['_source'][
#     #         'bucket'] + '.s3.amazonaws.com/' + each_res['_source']['objectKey'].replace(' ', "+")

#     # logger.info("res:{}".format(res))

#     return {
#         'statusCode': 200,
#         # 'body': json.dumps(res),
#         # 'headers': {
#         #     "Access-Control-Allow-Origin": "*",
#         #     "Access-Control-Allow-Credentials": True
#         # }
#     }

def get_labels(text):
    # event-> show me cat 
    region = 'us-east-1'
    client = boto3.client('lex-runtime')
    response =client.post_text(
        botName='photobo',
        botAlias='test',
        userId='testuser',
        inputText=text
    )
    print("lex-response", response)

    # labels = []
    # if 'slots' not in response:
    #     # print("No photo collection for query {}".format(query))
    #     pass
    # else:
    #     print("slot: ", response['slots'])
    #     slot_val = response['slots']
    #     for key, value in slot_val.items():
    #         if value != None:
    #             labels.append(value)
    return response
