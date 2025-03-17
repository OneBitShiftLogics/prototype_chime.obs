import json
import boto3
import os
from datetime import datetime

# Initialize AWS clients
chime = boto3.client("chime-sdk-meetings")
dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def lambda_handler(event, context):
    print("Lambda 'end_meeting' invoked with event:", event)
    
    meeting_id = event["pathParameters"]["meeting_id"]
    print("Processing meeting end for MeetingId:", meeting_id)

    # Retrieve meeting details from DynamoDB
    response = table.get_item(Key={"MeetingId": meeting_id})
    if "Item" not in response:
        print("Meeting not found in DynamoDB for MeetingId:", meeting_id)
        return {"statusCode": 404, "body": json.dumps({"error": "Meeting not found"})}

    start_time = response["Item"]["StartTime"]
    end_time = int(datetime.utcnow().timestamp())
    duration = end_time - start_time
    print(f"Meeting duration computed: {duration} seconds (Start: {start_time}, End: {end_time})")

    # Delete the meeting from Chime
    print("Deleting meeting from Chime with MeetingId:", meeting_id)
    chime.delete_meeting(MeetingId=meeting_id)
    print("Meeting deleted from Chime.")

    print("Lambda 'end_meeting' completed. Returning response.")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "meeting_id": meeting_id,
            "duration_seconds": duration,
            "end_time": end_time
        })
    }
