#!/bin/bash

# Create a dist directory
rm -rf dist
mkdir -p dist

# Install dependencies
pip install -r requirements.txt -t dist/

# Copy the lambda function code
cp -r lambda_function/* dist/

# Create a zip file
(cd dist && zip -r ../lambda_function.zip .)

echo "Created lambda_function.zip"