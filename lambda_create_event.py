import json
import boto3
from datetime import datetime
import uuid # For unique IDs for events

# Initialize S3 and SNS clients
s3_client = boto3.client('s3')
sns_client = boto3.client('sns')

# >>> IMPORTANT: Replace with your S3 bucket name from Section 1 of README.md <<<
S3_BUCKET_NAME = 'your-name-bucket' 
EVENTS_JSON_KEY = 'events.json'

# >>> IMPORTANT: Replace with your SNS Topic ARN from Section 3 of README.md <<<
SNS_TOPIC_ARN = 'arn:aws:sns:YOUR_AWS_REGION:YOUR_ACCOUNT_ID:EventAnnouncementsTopic' 

# >>> IMPORTANT: Replace with your S3 Static Website Endpoint URL from Section 1 of README.md <<<
# This URL is used in the email notification message.
YOUR_S3_STATIC_WEBSITE_URL = 'http:// .......................' (replace)

def lambda_handler(event, context):
    print(f"Received raw event: {json.dumps(event, indent=2)}") # Print full raw event for debugging
    
    try:
        parsed_data = {}
        # Check if it's a direct JSON payload OR if it's wrapped in 'body' from API Gateway Proxy Integration
        if 'body' in event and isinstance(event['body'], str):
            try:
                parsed_data = json.loads(event['body'])
                print("Parsed data from event['body']")
            except json.JSONDecodeError:
                print("Error: event['body'] is not valid JSON.")
                return {
                    'statusCode': 400,
                    'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                    'body': json.dumps({'message': 'Invalid JSON in request body.'})
                }
        else:
            # If 'body' is not a string, or not present, assume event itself is the data (e.g., from Lambda console test)
            parsed_data = event
            print("Parsed data directly from event object")

        title = parsed_data.get('title')
        date = parsed_data.get('date')
        description = parsed_data.get('description')

        if not all([title, date, description]):
            print(f"Validation error: Missing title={title}, date={date}, description={description}")
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                'body': json.dumps({'message': 'Missing event details (title, date, description).'})
            }
        
        # --- 1. Get existing events.json from S3 ---
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=EVENTS_JSON_KEY)
            existing_events = json.loads(response['Body'].read().decode('utf-8'))
            print("Successfully retrieved existing events.json from S3.")
        except s3_client.exceptions.NoSuchKey:
            existing_events = []
            print(f"{EVENTS_JSON_KEY} not found in S3. Starting with an empty list.")
        except Exception as e:
            print(f"Error reading events.json from S3: {e}")
            import traceback
            traceback.print_exc()
            return {
                'statusCode': 500,
                'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                'body': json.dumps({'message': f'Error reading existing events: {str(e)}'})
            }

        # --- 2. Add the new event ---
        new_event = {
            "id": str(uuid.uuid4()), # Generate a unique ID for the event
            "title": title,
            "date": date,
            "description": description
        }
        existing_events.append(new_event)

        # Sort events by date for better display (optional)
        existing_events.sort(key=lambda x: x.get('date', ''))
        print(f"New event added to list: {new_event['title']}")

        # --- 3. Upload updated events.json back to S3 ---
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=EVENTS_JSON_KEY,
                Body=json.dumps(existing_events, indent=4),
                ContentType='application/json'
            )
            print(f"Successfully updated {EVENTS_JSON_KEY} in S3.")
        except Exception as e:
            print(f"Error writing updated events.json to S3: {e}")
            import traceback
            traceback.print_exc()
            return {
                'statusCode': 500,
                'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                'body': json.dumps({'message': f'Error writing updated events to S3: {str(e)}'})
            }

        # --- 4. Publish event announcement to SNS ---
        sns_subject = f"New Event Announcement: {title} on {date}"
        sns_message = (
            f"A new event has been added to our system!\n\n"
            f"Title: {title}\n"
            f"Date: {date}\n"
            f"Description: {description}\n\n"
            f"Visit our website for more details: {YOUR_S3_STATIC_WEBSITE_URL}"
        )
        
        try:
            sns_client.publish(
                TopicArn=SNS_TOPIC_ARN,
                Message=sns_message,
                Subject=sns_subject
            )
            print("Successfully published new event announcement to SNS.")
        except Exception as e:
            print(f"Error publishing to SNS: {e}. This might be due to incorrect ARN or permissions.")
            import traceback
            traceback.print_exc()
            # We'll still return success for the API call if S3 update worked,
            # but log the SNS error.
            pass 
            
        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'message': 'Event created and announcement sent successfully!'})
        }

    except json.JSONDecodeError:
        print("Final error: Invalid JSON in request body (outer try-catch).")
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'message': 'Invalid JSON in request body.'})
        }
    except Exception as e:
        print(f"Unhandled error in createEventFunction (outer try-catch): {e}")
        import traceback
        traceback.print_exc() # Print full stack trace for better debugging
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'message': f'An unexpected error occurred: {str(e)}'})
        }
