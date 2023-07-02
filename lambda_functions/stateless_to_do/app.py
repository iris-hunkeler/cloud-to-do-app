import json

# import requests


def lambda_handler(event, context):
    """Expect a to do event and return it"""

    description = event['description']
    due_date = event['due_date']

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": f"You should do '{description}' by {due_date}",
        }),
    }
