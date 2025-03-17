import json
import boto3
import os
from datetime import datetime

chime = boto3.client("chime-sdk-meetings")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    meeting_id = event["pathParameters"]["meeting_id"]

    # Retrieve meeting details from DynamoDB
    response = table.get_item(Key={"MeetingId": meeting_id})
    if "Item" not in response:
        return {"statusCode": 404, "body": json.dumps({"error": "Meeting not found"})}

    start_time = response["Item"]["StartTime"]
    end_time = int(datetime.utcnow().timestamp())
    duration = end_time - start_time

    # Delete the meeting from Chime
    chime.delete_meeting(MeetingId=meeting_id)

    return {
        "statusCode": 200,
        "body": json.dumps({
            "meeting_id": meeting_id,
            "duration_seconds": duration,
            "end_time": end_time
        })
    }
