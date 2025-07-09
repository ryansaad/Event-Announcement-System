# Event-Announcement-System
This project demonstrates a real-time event announcement system built entirely using AWS serverless services: AWS S3 for static website hosting, AWS Lambda for backend logic, AWS SNS for fan-out email notifications, and AWS API Gateway as the public API endpoint. 


## Features

* **Static Website Hosting:** Frontend served directly from an S3 bucket.
* **Event Submission:** Users can submit new event titles, dates, and descriptions via a web form.
* **Real-time Event Display:** New events are immediately added to the `events.json` file in S3 and displayed on the website after submission.
* **Email Subscription:** Users can subscribe to receive email notifications for new events.
* **Real-time Announcements:** Confirmed subscribers receive an email notification whenever a new event is added.
* **Serverless Architecture:** Fully managed services (S3, Lambda, API Gateway, SNS) for high scalability, reliability, and cost-effectiveness.

## Getting Started

Follow these steps to deploy and run the Real-time Event Announcement System in your AWS account.

### Prerequisites

* An active AWS Account.
* AWS CLI (Optional, but recommended for local interaction).
* Basic understanding of AWS S3, Lambda, API Gateway, and SNS.
* 
### Step-by-Step Deployment

#### 1. AWS S3 (Website Hosting)

This is where your frontend files will live.

1.  **Create an S3 Bucket:**
    * Go to the S3 console.
    * Click "Create bucket".
    * **Bucket name:** Choose a unique name 
    * **AWS Region:** Select your desired region 
    * Click "Create bucket".

2.  **HTML,CSS and event.json File Content**
    * See the index.html style.css and events.json file in the repository  

3.  **Upload Files to S3:**
    * In your S3 bucket, click "Upload".
    * Add `index.html`, `style.css`, and `events.json`.
    * Click "Upload".
      
4.  **Enable Static Website Hosting:**
    * Go to your bucket's "Properties" tab.
    * Scroll to "Static website hosting" and click "Edit".
    * Select "Enable", "Host a static website".
    * **Index document:** `index.html`
    * Click "Save changes".
    * Note your **Bucket website endpoint URL This will be `YOUR_S3_STATIC_WEBSITE_ENDPOINT` in `index.html`.

5.  **Set Bucket Policy for Public Read Access:**
    * Go to your bucket's "Permissions" tab.
    * Under "Block Public Access (bucket settings)", ensure **all four boxes are UNCHECKED**. Save changes (type `confirm`).
    * Scroll to "Bucket policy" and click "Edit".
    * Paste the following policy, replacing `YOUR_BUCKET_NAME` with your actual bucket name:
        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
                }
            ]
        }
        ```
    * Click "Save changes".

#### 2. AWS IAM (Lambda Permissions)

You'll create two roles that your Lambda functions will assume.

1.  **Create `LambdaSubscribeRole`:**
    * Go to the IAM console -> "Roles" -> "Create role".
    * **Trusted entity:** "AWS service" -> "Lambda".
    * **Permissions:** Search and attach `AmazonSNSFullAccess` and `CloudWatchLogsFullAccess`.
    * **Role name:** `LambdaSubscribeRole`
    * Click "Create role".
2.  **Create `EventCreationLambdaRole`:**
    * Go to the IAM console -> "Roles" -> "Create role".
    * **Trusted entity:** "AWS service" -> "Lambda".
    * **Permissions:** Search and attach `AmazonS3FullAccess`, `AmazonSNSFullAccess`, and `CloudWatchLogsFullAccess`.
    * **Role name:** `EventCreationLambdaRole`
    * Click "Create role".

#### 3. AWS SNS (Notification Topic)

This is the channel for your event announcements.

1.  **Create an SNS Topic:**
    * Go to the SNS console -> "Topics" -> "Create topic".
    * **Type:** "Standard".
    * **Name:** `EventAnnouncementsTopic`
    * Click "Create topic".
    * **Note the Topic ARN** . You'll need this for your Lambda functions.

#### 4. AWS Lambda (Functions)

You'll create two Python Lambda functions.

1.  **Create `subscribeToSNSFunction`:**
    * Go to the Lambda console -> "Functions" -> "Create function".
    * **Function name:** `subscribeToSNSFunction`
    * **Runtime:** `Python 3.9` (or latest)
    * **Execution role:** "Use an existing role" -> `LambdaSubscribeRole`.
    * Click "Create function".
    * Go to the code files for the functions . **Remember to replace `SNS_TOPIC_ARN` placeholder.**
    * Click "Deploy".
2.  **Create `createEventFunction`:**
    * Go to the Lambda console -> "Functions" -> "Create function".
    * **Function name:** `createEventFunction`
    * **Runtime:** `Python 3.9` (or latest)
    * **Execution role:** "Use an existing role" -> `EventCreationLambdaRole`.
    * Click "Create function".
    * Paste the code from the python files for the function **Remember to replace `S3_BUCKET_NAME`, `SNS_TOPIC_ARN`, and `YOUR_S3_STATIC_WEBSITE_URL` placeholders.**
    * Click "Deploy".

#### 5. AWS API Gateway (REST API)

This creates the public endpoints for your Lambda functions.

1.  **Create a REST API:**
    * Go to the API Gateway console -> "REST API" -> "Build".
    * Select "New API".
    * **API name:** `EventAnnouncementAPI`
    * Click "Create API".
2.  **Create `/subscribe` Resource and POST Method:**
    * Select the root resource (`/`).
    * "Actions" -> "Create Resource".
    * **Resource Name:** `subscribe`
    * Click "Create Resource".
    * With `/subscribe` selected, "Actions" -> "Create Method".
    * Select `POST`.
    * **Integration type:** "Lambda Function".
    * **Use Lambda proxy integration:** Check this box.
    * **Lambda Function:** Type `subscribeToSNSFunction` and select.
    * Click "Save" and "OK" to grant Lambda permissions.
    * **Enable CORS:** With `/subscribe` selected, "Actions" -> "Enable CORS".
        * **Access-Control-Allow-Origin:** Enter your **S3 Bucket website endpoint URL** (e.g., `http://your-name-event-announcement-bucket.s3-website-us-east-1.amazonaws.com`). **Do NOT include a trailing slash.**
        * Ensure `POST` and `OPTIONS` methods are allowed.
        * Click "Enable CORS and replace existing CORS headers".
3.  **Create `/create-event` Resource and POST Method:**
    * Select the root resource (`/`).
    * "Actions" -> "Create Resource".
    * **Resource Name:** `create-event`
    * Click "Create Resource".
    * With `/create-event` selected, "Actions" -> "Create Method".
    * Select `POST`.
    * **Integration type:** "Lambda Function".
    * **Use Lambda proxy integration:** Check this box.
    * **Lambda Function:** Type `createEventFunction` and select.
    * Click "Save" and "OK" to grant Lambda permissions.
    * **Enable CORS:** With `/create-event` selected, "Actions" -> "Enable CORS".
        * **Access-Control-Allow-Origin:** Enter your **S3 Bucket website endpoint URL**.
        * Ensure `POST` and `OPTIONS` methods are allowed.
        * Click "Enable CORS and replace existing CORS headers".
4.  **Deploy API:**
    * "Actions" -> "Deploy API".
    * **Deployment stage:** `[New Stage]`
    * **Stage name:** `prod`(give it any name)
    * Click "Deploy".
    * **Note the "Invoke URL"** 

#### 6. Frontend (`index.html`) Update

1.  **Download `index.html`** from your S3 bucket.
2.  Open it in a text editor.
3.  Locate the JavaScript section and replace the placeholders:
    * `const API_GATEWAY_CREATE_EVENT_URL = 'YOUR_API_GATEWAY_CREATE_EVENT_URL';`
        * Replace with your API Gateway Invoke URL + `/create-event` (e.g., `https://abcdef123.execute-api.us-east-
          1.amazonaws.com/prod/create-event`).
    * `const API_GATEWAY_SUBSCRIBE_URL = 'YOUR_API_GATEWAY_SUBSCRIBE_URL';`
        * Replace with your API Gateway Invoke URL + `/subscribe` (e.g., `https://abcdef123.execute-api.us-east-
          1.amazonaws.com/prod/subscribe`).
    * `const S3_STATIC_WEBSITE_ENDPOINT = 'YOUR_S3_STATIC_WEBSITE_ENDPOINT';`
        * Replace with your S3 Bucket website endpoint URL (e.g., `http://your-name-event-announcement-bucket.s3-website-us-east-
          1.amazonaws.com`).
          
4.  **Save `index.html` and upload it back to your S3 bucket, overwriting the existing file.**

#### 7. Testing

1.  **Open your website** in a browser (use the S3 Bucket website endpoint URL). 
2.  **Subscribe:** Go to the "Subscribe for Notifications" section, enter your email, click "Subscribe". Check your email for the AWS SNS confirmation and **click the confirmation link**.
3.  **Create Event:** Go to the "Submit a New Event" section, fill in details, click "Submit Event".
4.  **Verify:**
    * The new event should appear on the website list.
    * You should receive an email announcement for the new event in your subscribed inbox.
    * You can also check the `events.json` file in your S3 bucket (download it) to ensure the event was added there.

---

## Important Notes & Troubleshooting

* **CORS:** If you see "CORS" errors in your browser's developer console (F12 -> Console/Network), double-check your API Gateway CORS settings. Ensure `Access-Control-Allow-Origin` exactly matches your S3 website URL.
* **Caching:** Browsers and S3 can cache content. If updates don't appear immediately, try a hard refresh (Ctrl+F5 or Cmd+Shift+R) or clear your browser's cache. Testing in an Incognito/Private window helps.
* **SNS Email Confirmation:** Remember, email subscriptions to SNS topics require a mandatory confirmation step by clicking a link in an email sent by AWS. Without confirmation, you will not receive messages.
* **CloudWatch Logs:** For any issues, check the CloudWatch logs for your Lambda functions. They provide detailed insights into what's happening during function execution (go to Lambda function -> Monitor tab -> View CloudWatch logs).

---
