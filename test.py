
import json
import requests
import os

# Upload the test image to the local S3 bucket
os.system("aws --endpoint-url http://localhost:9001 s3 cp test_image.png s3://my-bucket/users/u1/imgs/1.jpg")

# Prepare the payload for the Lambda function
payload = {
    "images": [
        {"bucket": "my-bucket", "key": "users/u1/imgs/1.jpg"}
    ],
    "scale": 4,
    "output": {"bucket": "output-bucket", "prefix": "users/u1/upscaled/"}
}

# Invoke the Lambda function
url = "http://localhost:9000/2015-03-31/functions/function/invocations"
response = requests.post(url, data=json.dumps(payload))

# Print the response
print(response.json())
