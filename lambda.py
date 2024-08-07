import boto3
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('FileUploads')
s3_client = boto3.client('s3', region_name='us-east-2')
ses_client = boto3.client('ses', region_name='us-east-2')

BUCKET_NAME = 'sumanthhbucket'
EMAIL_SOURCE = 'sallurisumanth05@gmail.com'  

def lambda_handler(event, context):
    logger.info(f'Received event: {json.dumps(event)}')
    
    try:
        unique_id = event['pathParameters']['unique_id']
        
        response = table.scan(
            FilterExpression='contains(file_url, :unique_id)',
            ExpressionAttributeValues={':unique_id': unique_id}
        )
        logger.info(f'DynamoDB scan response: {response}')

        if 'Items' in response and response['Items']:
            item = response['Items'][0]
            username = item['username']
            filename = item['filename']
            clicks = item['clicks']
            unique_links = item['file_url']

            email = None
            for key, value in unique_links.items():
                if value == unique_id:
                    email = key
                    break

            if email:
                clicks[email] = True

                table.update_item(
                    Key={'username': username, 'filename': filename},
                    UpdateExpression='SET clicks = :clicks',
                    ExpressionAttributeValues={':clicks': clicks}
                )

                if all(clicks.values()):
                    s3_client.delete_object(Bucket=BUCKET_NAME, Key=filename)
                    table.delete_item(Key={'username': username, 'filename': filename})

                pre_signed_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': BUCKET_NAME, 'Key': filename},
                    ExpiresIn=60
                )
                logger.info(f'Generated pre-signed URL: {pre_signed_url}')

                send_email(email, pre_signed_url)

                return {
                    'statusCode': 302,
                    'headers': {'Location': pre_signed_url},
                    'body': json.dumps('Redirecting to file...')
                }

        logger.error('Invalid link or record not found.')
        return {
            'statusCode': 400,
            'body': json.dumps('Invalid link.')
        }
    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error: {str(e)}')
        }

def send_email(email, pre_signed_url):
    try:
        response = ses_client.send_email(
            Source=EMAIL_SOURCE,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': 'Your File is Ready for Download'},
                'Body': {'Text': {'Data': f'You can download the file using this link: {pre_signed_url}'}}
            }
        )
        logger.info(f'Email sent to {email}, SES response: {response}')
    except Exception as e:
        logger.error(f'Error sending email to {email}: {str(e)}')
