---
# 🎬 Movie Poster Generator using Amazon Bedrock and AWS Lambda

This project demonstrates how to build a serverless application using AWS Lambda and Amazon Bedrock to generate AI-based movie poster designs. The posters are created using the **Stability Diffusion model** hosted on Amazon Bedrock and stored in an Amazon S3 bucket. The application exposes a REST API (via API Gateway) that accepts a prompt, generates an image, stores it, and returns a pre-signed URL to access the image.
---

## 🛠️ Architecture Overview

1. **Amazon S3** – Stores the AI-generated poster images.
2. **AWS Lambda** – Handles Bedrock inference, S3 upload, and URL generation.
3. **Amazon Bedrock** – Accesses the Stability Diffusion model to generate images from prompts.
4. **API Gateway** – REST interface to send prompts and retrieve image links.

![AWS Architecture Example](https://movie-poster-design-0101-abc.s3.us-east-1.amazonaws.com/Movie+Poster+Design+-+GenAI-v2.png)

---

## 📦 Features

- Accept prompt input via REST API.
- Generate poster image using Stability Diffusion model (Amazon Bedrock).
- Store generated image in S3.
- Return a pre-signed URL for secure access.
- Python-based AWS Lambda function using Boto3 SDK.

---

## 📁 Project Structure

```bash
.
├── lambda_function.py   # AWS Lambda handler function
├── README.md            # This file
```

---

## ✅ Prerequisites

- AWS Account with access to:

  - Amazon Bedrock (Titan Image Generator G1 model)
  - Amazon S3
  - AWS Lambda
  - API Gateway

- IAM role for Lambda with access to Bedrock and S3
- Python 3.11

---

## 🚀 Deployment Steps

### 1. Create an S3 Bucket

Go to the AWS Console and create a bucket, e.g., `movie-poster-design-01`.

### 2. Create Lambda Function

- Runtime: Python 3.11
- Name: `movie-poster-design-function`
- Increase **timeout** to **1 minute 3 seconds**.
- Attach temporary **AdministratorAccess** policy.
- Verify Boto3 version (`>=1.28.63`) inside Lambda:

```python
#1. import boto3
import boto3
print(boto3.__version__)

import json
import base64
import datetime

#2. Create client connection with Bedrock and S3 Services – Link
client_bedrock = boto3.client('bedrock-runtime')
client_s3 = boto3.client('s3')

def lambda_handler(event, context):
    # print("event: ", event)
#3. Store the input data (prompt) in a variable
    input_prompt=json.loads(event['body'])['prompt']
    print(input_prompt)

#4. Create a Request Syntax to access the Bedrock Service
    response_bedrock = client_bedrock.invoke_model(contentType='application/json', accept='application/json',modelId='amazon.titan-image-generator-v2:0',
       body=json.dumps({
        "taskType": "TEXT_IMAGE",
        "textToImageParams": {
            "text": input_prompt
        },
        "imageGenerationConfig": {
            "numberOfImages": 1,
            "height": 512,
            "width": 512,
            "cfgScale": 8.0,
            "seed": 0
        }
    }))
    print(response_bedrock)

#5. 5a. Retrieve from Dictionary, 5b. Convert Streaming Body to Byte using json load 5c. Print

    response_bedrock_byte=json.loads(response_bedrock['body'].read())
    print(response_bedrock_byte)
#6. 6a. Retrieve data with artifact key, 6b. Import Base 64, 6c. Decode from Base64
    response_bedrock_base64 = response_bedrock_byte['images'][0]
    response_bedrock_finalimage = base64.b64decode(response_bedrock_base64)
    print(response_bedrock_finalimage)

#7. 7a. Upload the File to S3 using Put Object Method – Link 7b. Import datetime 7c. Generate the image name to be stored in S3 - Link
    poster_name = 'poster_' + datetime.datetime.today().strftime('%Y-%m-%d-%H-%M-%S') + '.png'

    client_s3.put_object(
        Bucket='movie-poster-design-0101-abc',
        Body=response_bedrock_finalimage,
        Key=poster_name,
        ContentType='image/png'
    )

#8. Generate Pre-Signed URL
    generate_presigned_url = client_s3.generate_presigned_url('get_object', Params={'Bucket':'movie-poster-design-0101-abc','Key':poster_name}, ExpiresIn=3600)
    print(generate_presigned_url)
    return {
        'statusCode': 200,
        'body': generate_presigned_url
    }
```

### 4. Write Lambda Function Logic

Your Lambda handler should:

- Accept prompt from event
- Call Bedrock with Stability Diffusion model
- Decode image and upload to S3
- Generate a pre-signed S3 URL
- Return the URL

### 5. Set Up API Gateway

- Create a REST API
- POST method to trigger Lambda with JSON body: `{ "prompt": "a futuristic movie poster of a robot" }`
- Return the pre-signed URL from the Lambda response

---

## 🔁 Testing the API

You can test using [Postman](https://www.postman.com/) or `curl`.

### Example request:

```bash
POST https://<api-gateway-url>/generate
Content-Type: application/json

{
  "prompt": "a 1980s style sci-fi movie poster with neon lights"
}
```

### Example response:

```json
{
  "image_url": "https://movie-poster-design-0101-abc.s3.amazonaws.com/generated/abc123.jpg?X-Amz-SecurityToken=..."
}
```

---

## 📌 Notes

- **Bedrock access** must be enabled in your region/account.
- **S3 Pre-signed URLs** are time-limited and secure.
- Avoid long prompts to reduce generation time and prevent Lambda timeouts.
- For production, use more granular IAM policies and add input validation.

---

## 📷 Demo

![Poster Example](https://movie-poster-design-0101-abc.s3.us-east-1.amazonaws.com/poster_2025-07-06-07-06-38.png)

---

## 🧾 License

MIT License. Feel free to reuse and modify.

---
