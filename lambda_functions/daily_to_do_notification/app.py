
import boto3
from boto3.dynamodb.conditions import Attr
import json
import logging 
from datetime import date

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'to-do-table'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

topic_arn = '' # TODO: insert arn after creation


def lambda_handler(event, context):
    logger.info(f'event: {event}')
    
    toDos = getTodosDueToday()
    logger.info(f'toDos: {toDos}')
    sendNotification(f'You have {len(toDos)} To Do items due today!')
    
    return buildResponse(200, '')
   
def getTodosDueToday():
    today = date.today().strftime('%Y-%m-%d')
    logger.info(f'today: {today}')
    
    try:
        response = table.scan(
            FilterExpression=Attr("dueDate").eq(today)
        )
        
        result = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(
                FilterExpression=Attr("dueDate").eq(today),
                ExclusiveStartKey=response['LastEvaluatedKey']
            )
            result.extend(response['Items'])

        return result
    except:
        logger.exception('Log it here for now')
        
    
def sendNotification(message):
    sns = boto3.client('sns')
    sns.publish(
            TopicArn=topic_arn,
            Message=message
        )
    
def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'ContentType': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }
    if body is not None:
        response['body'] = json.dumps(body)
    return response

