# ☁️ Cloud File Sharing Tool

This is a **secure file-sharing tool** built using **Flask**, **AWS S3**, **DynamoDB**, **Lambda**, and **SES**. The tool enables users to securely upload and share files with recipients. The system includes features such as user authentication, file upload to S3, email notifications, click tracking with DynamoDB, and automatic file deletion once all recipients have accessed the file.

## 🚀 Features
- **User Authentication**: Secure login and registration process.
- **File Upload**: Upload files to AWS S3 for secure storage.
- **Email Notifications**: Notify recipients via email when a new file is shared using AWS SES.
- **Click Tracking**: Track file access using DynamoDB to keep a record of who has accessed the file.
- **Automatic File Deletion**: Automatically delete files from S3 once all recipients have accessed them.

## 🛠️ Technologies Used
- **Flask**: For building the web application and handling user requests.
- **AWS S3**: For storing and managing files securely.
- **AWS DynamoDB**: For tracking file access by recipients.
- **AWS Lambda**: For serverless functions, such as sending email notifications and processing file deletions.
- **AWS SES**: For sending email notifications to recipients.

## 📷 Project Preview
![Cloud File Sharing Tool Screenshot](https://via.placeholder.com/800x400)  
*(Replace with an actual screenshot of your project)*

## 📂 Installation & Usage
1. **Clone the repository:**
   ```sh
   git clone https://github.com/yourusername/cloud-file-sharing-tool.git
2. Install Dependencies: Install required libraries using pip:
   ```
   pip install -r requirements.txt
3. Set Up AWS Credentials: Make sure to configure AWS CLI with your AWS credentials:
   ```
   aws configure
4. Run the Flask Application: Start the Flask development server:
   ```
   python app.py
5. Access the Application: Open a web browser and go to http://127.0.0.1:5000/ to access the file-sharing tool.

🔧 Configuration
Set up your AWS S3 bucket and configure AWS SES for email notifications.
Update the DynamoDB table to track user file access.
Customize the email template in AWS SES as needed.

🎯 Future Improvements
Add a more advanced authentication system (e.g., OAuth, Google login).
Implement file versioning and management.
Add support for large file uploads using AWS S3 pre-signed URLs.
Provide more advanced file tracking and analytics.

📌 Author
Sumanth Salluri
🔗 GitHub: sallurisumanth

