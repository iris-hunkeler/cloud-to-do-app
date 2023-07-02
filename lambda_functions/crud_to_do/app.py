import boto3
import json
import logging 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTableName = 'to-do-table'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTableName)

getMethod = 'GET'
postMethod = 'POST'
putMethod = 'PUT'
deleteMethod = 'DELETE'
toDosPath = '/to-dos'

def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    if httpMethod == getMethod and path == toDosPath:
        response = getAllTodos()
    elif httpMethod == getMethod and path.startswith(toDosPath):
        response = getTodo(event['pathParameters']['id'])
    elif httpMethod == putMethod and path == toDosPath:
        response = saveTodo(json.loads(event['body']))
    elif httpMethod == deleteMethod and path.startswith(toDosPath):

        response = deleteTodo(event['pathParameters']['id'])
    else:
        response = buildResponse(404, 'Not Found')
 
    return response

def getAllTodos():
    try:
        response = table.scan()
        result = response['Items']

        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        body = {
            'todos': result
        }
        return buildResponse(200, body)
    except:
        logger.exception('Log it here for now')
        
def getTodo(todoId):
    try:
        response = table.get_item(
            Key={
                'id': todoId
            }
        )
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        else:
            return buildResponse(404, {'Message': 'To do: %s not found' % todoId})
    except:
        logger.exception('Log it here for now')
        
def saveTodo(requestBody):
    try:
        table.put_item(Item=requestBody)
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        return buildResponse(200, body)
    except:
        logger.exception('Log it here for now')

def deleteTodo(todoId):
    try:
        response = table.delete_item(
            Key = {
                'id': todoId
            },
            ReturnValues='ALL_OLD'
        )
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }
        return buildResponse(200, body)
    except:
        logger.exception('Log it here for now')


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