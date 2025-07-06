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
#3. Store the input data (prompt) in a variable
    input_prompt=event['prompt']
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