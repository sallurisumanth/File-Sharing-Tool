from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import boto3
import os
from werkzeug.utils import secure_filename
import logging
import uuid

app = Flask(__name__)
app.secret_key = 'Ut/WvLX/Tfsuyota2mddnxL9cV60MspJer/YEJI0'
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

s3_client = boto3.client('s3', region_name='us-east-2')
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')
table = dynamodb.Table('FileUploads')
BUCKET_NAME = 'sumanthhbucket'
users = {'file': 'salluri@123'}

logging.basicConfig(level=logging.DEBUG)

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] in users and users[request.form['username']] == request.form['password']:
            session['username'] = request.form['username']
            return redirect(url_for('upload'))
        flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        emails, file = request.form.get('emails').split(','), request.files['file']
        if not emails or not file or len(emails) > 5:
            flash('Invalid input or too many recipients.', 'danger')
            return redirect(url_for('upload'))

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        try:
            # Upload the file to S3
            s3_client.upload_file(file_path, BUCKET_NAME, filename)
            os.remove(file_path)

            unique_links = {email: str(uuid.uuid4()) for email in emails}
            clicks = {email: False for email in emails}

            # Store file information in DynamoDB
            table.put_item(Item={
                'ec2-user': session['username'], 
                'filename': filename, 
                'file_url': unique_links,
                'emails': emails,
                'clicks': clicks
            })

            # Send emails
            for email, unique_id in unique_links.items():
                send_email(email, unique_id, filename)

            flash('File uploaded and emails sent successfully!', 'success')
        except Exception as e:
            logging.error(f'Error during file upload or email sending: {str(e)}')
            flash(f'An error occurred during file upload or email sending: {str(e)}', 'danger')
        return redirect(url_for('upload'))
    
    return render_template('upload.html')

@app.route('/download/<unique_id>', methods=['GET'])
def download_file(unique_id):
    logging.debug(f'Processing download for unique_id: {unique_id}')
    try:
        response = table.scan(FilterExpression='contains(file_url, :unique_id)', ExpressionAttributeValues={':unique_id': unique_id})
        item = response['Items'][0] if 'Items' in response and response['Items'] else None

        if not item:
            logging.error('Invalid link or record not found.')
            return 'Invalid link.'

        email = next((key for key, value in item['file_url'].items() if value == unique_id), None)
        if email:
            item['clicks'][email] = True
            table.update_item(Key={'ec2-user': item['ec2-user'], 'filename': item['filename']}, UpdateExpression='SET clicks = :clicks', ExpressionAttributeValues={':clicks': item['clicks']})
            
            if all(item['clicks'].values()):
                s3_client.delete_object(Bucket=BUCKET_NAME, Key=item['filename'])
                table.delete_item(Key={'ec2-user': item['ec2-user'], 'filename': item['filename']})
            
            pre_signed_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': item['filename']}, ExpiresIn=60)
            logging.debug(f'Generated pre-signed URL: {pre_signed_url}')
            return redirect(pre_signed_url)
    except Exception as e:
        logging.error(f'Error during download process: {str(e)}')
        return 'An error occurred while processing your request.'

def send_email(email, unique_id, filename):
    try:
        ses_client = boto3.client('ses', region_name='us-east-2')
        pre_signed_url = s3_client.generate_presigned_url('get_object', Params={'Bucket': BUCKET_NAME, 'Key': filename}, ExpiresIn=3600)
        ses_client.send_email(Source='sallurisumanth05@gmail.com', Destination={'ToAddresses': [email]}, Message={'Subject': {'Data': 'File Shared with You'}, 'Body': {'Text': {'Data': f'You can download the file from: {pre_signed_url}'}}})
        logging.info(f'Email sent to {email}')
    except Exception as e:
        logging.error(f'Error sending email to {email}: {str(e)}')

if __name__ == '__main__':
    app.run(debug=True)
