# Oodle Lambda - Image Enhancement

This project contains an AWS Lambda function that enhances images from an S3 bucket using Real-ESRGAN.

## Prerequisites

* Python 3.x
* pip
* AWS CLI
* Docker

## Functionality

The Lambda function is triggered by a request containing information about the images to be enhanced.

**Request Body:**

```json
{
  "images": [
    {"bucket": "my-bucket", "key": "users/u1/imgs/1.jpg"},
    {"bucket": "my-bucket", "key": "users/u1/imgs/2.png"}
  ],
  "profilePic": {"bucket": "my-bucket", "key": "users/u1/profile.jpg"},
  "scale": 4,
  "output": {"bucket": "my-bucket", "prefix": "users/u1/upscaled/"}
}
```

**Success Response:**

```json
{
  "results": [
    {
      "inputKey": "users/u1/imgs/1.jpg",
      "outputKey": "users/u1/upscaled/1_x4.jpg",
      "width": 2048,
      "height": 2048,
      "mime": "image/jpeg"
    }
  ],
  "profilePicResult": {
    "inputKey": "users/u1/profile.jpg",
    "outputKey": "users/u1/upscaled/profile_x4.jpg",
    "width": 1024,
    "height": 1024,
    "mime": "image/jpeg"
  }
}
```

## Setup

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   **Note:** The dependencies for this project, especially `torch` and `realesrgan`, are large. The total size of the deployment package may exceed the AWS Lambda deployment package size limit of 250 MB (unzipped). For production environments, it is highly recommended to use **AWS Lambda Layers** to manage these dependencies.

## Local Testing

You can test the Lambda function locally using Docker and Docker Compose.

1. **Build and start the containers:**

   ```bash
   docker-compose up --build
   ```

2. **Create the test image:**

   In a separate terminal, run the following commands. You will need to have `Pillow` and `requests` installed (`python3 -m pip install Pillow requests`).

   ```bash
   python3 create_test_image.py
   ```

3. **Run the test script:**

   ```bash
   python3 test.py
   ```

   This will upload a test image to the local MinIO (S3) instance, invoke the Lambda function, and print the response.

## Deployment

1. **Run the deployment script:**

   ```bash
   ./deploy.sh
   ```

2. **Upload the `lambda_function.zip` file to AWS Lambda.**

   You can do this through the AWS Management Console or by using the AWS CLI.

   **AWS CLI Example:**

   ```bash
   aws lambda create-function --function-name oodle-lambda-enhancement \
       --runtime python3.9 \
       --zip-file fileb://lambda_function.zip \
       --handler lambda_function.lambda_handler \
       --role <your-iam-role-arn> \
       --timeout 300 \
       --memory-size 1024
   ```

   **Important Notes:**
   * Replace `<your-iam-role-arn>` with the ARN of an IAM role that has the necessary permissions.
   * The `timeout` and `memory-size` may need to be adjusted based on the size of the images being processed.
   * **IAM Role Permissions:** The IAM role used by this Lambda function needs the following permissions:
     * `s3:GetObject` on the source bucket.
     * `s3:PutObject` on the destination bucket.
     * `logs:CreateLogGroup`, `logs:CreateLogStream`, `logs:PutLogEvents` for CloudWatch logging.

## Invocation

You can invoke the Lambda function using the AWS CLI, SDKs, or by setting up an API Gateway trigger.

**AWS CLI Invocation Example:**

```bash
aws lambda invoke --function-name oodle-lambda-enhancement --payload file://payload.json response.json
```

Where `payload.json` contains the request body.
# oodle_lambda
