import json
import boto3
import os
import requests
import uuid

chime = boto3.client("chime-sdk-meetings")
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "ChimeMeetingsTable")
table = dynamodb.Table(table_name)

AUDIO_API_URL = "https://api.murf.ai/v1/speech/generate"  # Replace with your actual API URL

def lambda_handler(event, context):
    bot_name = event["pathParameters"]["bot_name"]
    meeting_id = str(uuid.uuid4())

    # Create a Chime Meeting
    meeting_response = chime.create_meeting(
        ClientRequestToken=meeting_id,
        MediaRegion="us-east-1"
    )
    meeting = meeting_response["Meeting"]

    # Create a bot attendee
    bot_attendee = chime.create_attendee(
        MeetingId=meeting["MeetingId"],
        ExternalUserId=bot_name
    )["Attendee"]

    # Store meeting details in DynamoDB
    table.put_item(Item={
        "MeetingId": meeting["MeetingId"],
        "BotAttendeeId": bot_attendee["AttendeeId"],
        "StartTime": int(event["requestContext"]["requestTimeEpoch"])
    })

    # Request an audio file from Murf.ai
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "api-key": "ap2_4ab5f867-29da-4f2d-9f2e-b7c1fdc6d0c2"
    }
    payload = json.dumps({
        "voiceId": "en-IN-aarav",
        "style": "Conversational",
        "text": f"Hello, I am {bot_name}. Welcome!",
        "rate": 0,
        "pitch": 0,
        "sampleRate": 48000,
        "format": "MP3",
        "channelType": "MONO",
        "pronunciationDictionary": {},
        "encodeAsBase64": False,
        "variation": 1,
        "audioDuration": 0,
        "modelVersion": "GEN2",
        "multiNativeLocale": "en-IN"
    })

    audio_response = requests.post(AUDIO_API_URL, headers=headers, data=payload)
    audio_data = audio_response.json()
    audio_url = audio_data.get("audioFile")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "meeting": meeting,
            "bot_attendee": bot_attendee,
            "join_url": f"https://app.chime.aws/meetings/{meeting['MeetingId']}",
            "audio_url": audio_url
        })
    }
