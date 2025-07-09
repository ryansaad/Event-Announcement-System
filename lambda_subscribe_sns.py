import json
import boto3

# Initialize SNS client
sns_client = boto3.client('sns')

# >>> IMPORTANT: Replace with your SNS Topic ARN from Section 3 of README.md <<<
SNS_TOPIC_ARN = 'arn:aws:sns:YOUR_AWS_REGION:YOUR_ACCOUNT_ID:EventAnnouncementsTopic' 

def lambda_handler(event, context):
    print(f"Received event: {json.dumps(event)}")
    
    try:
        # API Gateway sends the request body as a string when using Proxy Integration
        if 'body' in event and isinstance(event['body'], str):
            body = json.loads(event['body'])
        else:
            # Fallback if 'body' is not present or not a string (e.g., direct Lambda test)
            body = event 
        
        email = body.get('email')

        if not email:
            print("Validation error: Email address is missing.")
            return {
                'statusCode': 400,
                'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
                'body': json.dumps({'message': 'Email address is required.'})
            }

        # Subscribe the email to the SNS topic
        response = sns_client.subscribe(
            TopicArn=SNS_TOPIC_ARN,
            Protocol='email',
            Endpoint=email
        )
        
        print(f"SNS subscribe response: {response}")

        return {
            'statusCode': 200,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'message': f'Successfully subscribed {email}. Please check your email for confirmation.'})
        }

    except json.JSONDecodeError:
        print("Error decoding JSON body.")
        return {
            'statusCode': 400,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'message': 'Invalid JSON in request body.'})
        }
    except Exception as e:
        print(f"Unhandled error in subscribeToSNSFunction: {e}")
        import traceback
        traceback.print_exc() # Print full stack trace for better debugging
        return {
            'statusCode': 500,
            'headers': { 'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*' },
            'body': json.dumps({'message': f'Failed to subscribe: {str(e)}'})
        }
