import json
import boto3
import os
import urllib.request
import uuid

# Initialize AWS clients
chime = boto3.client("chime-sdk-meetings")
dynamodb = boto3.resource("dynamodb")
table_name = os.environ.get("TABLE_NAME", "ChimeMeetingsTable")
table = dynamodb.Table(table_name)

# Murf API URL (replace with your actual API URL if different)
AUDIO_API_URL = "https://api.murf.ai/v1/speech/generate"

def lambda_handler(event, context):
    print("Lambda 'start_meeting' invoked with event:", event)
    
    bot_name = event["pathParameters"]["bot_name"]
    meeting_id = str(uuid.uuid4())
    print("Generated meeting ID:", meeting_id)

    # Create a Chime Meeting
    print("Creating a Chime meeting...")
    meeting_response = chime.create_meeting(
        ClientRequestToken=meeting_id,
        MediaRegion="us-east-1"
    )
    meeting = meeting_response["Meeting"]
    print("Meeting created:", meeting)

    # Create a bot attendee
    print(f"Creating bot attendee for bot name: {bot_name}")
    bot_attendee = chime.create_attendee(
        MeetingId=meeting["MeetingId"],
        ExternalUserId=bot_name
    )["Attendee"]
    print("Bot attendee created:", bot_attendee)

    # Store meeting details in DynamoDB
    print("Storing meeting details in DynamoDB table:", table_name)
    table.put_item(Item={
        "MeetingId": meeting["MeetingId"],
        "BotAttendeeId": bot_attendee["AttendeeId"],
        "StartTime": int(event["requestContext"]["requestTimeEpoch"])
    })

    # Prepare payload for Murf.ai API request
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
    data = payload.encode("utf-8")

    # Build and send the HTTP POST request using urllib
    req = urllib.request.Request(AUDIO_API_URL, data=data, headers=headers, method="POST")
    try:
        print("Sending request to Murf API...")
        with urllib.request.urlopen(req) as response:
            response_body = response.read().decode("utf-8")
            print("Murf API response:", response_body)
            audio_data = json.loads(response_body)
            audio_url = audio_data.get("audioFile")
    except Exception as e:
        print("Error during Murf API call:", e)
        audio_url = None

    print("Lambda 'start_meeting' completed. Returning response.")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "meeting": meeting,
            "bot_attendee": bot_attendee,
            "join_url": f"https://app.chime.aws/meetings/{meeting['MeetingId']}",
            "audio_url": audio_url
        })
    }
