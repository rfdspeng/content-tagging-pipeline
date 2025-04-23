#!/bin/bash

# https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/create-function.html

# Exit early if any commands return non-zero
set -e

# Set environment variables
# .env must include ECR_LINK, ROLE_ARN
# ECR_LINK = <account-id>.dkr.ecr.<region>.amazonaws.com
# ROLE_ARN is the ARN of the role you want to associate with your Lambda function
source .env
AWS_PROFILE_NAME=beamdata # If Beam Data credentials are not your default profile
FUNCTION_NAME=content-tagging-lms-v7
ECR_REPO="content-tagging/content-tagging-lms:v7" # ECR namespace and repo name
TIMEOUT=600 # In seconds
MEMORY=3000 # In MB
EPHEMERAL_STORAGE=2000 # In MB
COLLECTION_NAME=test_collection

aws lambda create-function --profile $AWS_PROFILE_NAME \
    --function-name $FUNCTION_NAME \
    --role $ROLE_ARN \
    --package-type Image \
    --code ImageUri="${ECR_LINK}/${ECR_REPO}" \
    --timeout $TIMEOUT \
    --memory-size $MEMORY \
    --ephemeral-storage Size=$EPHEMERAL_STORAGE \
    --environment Variables="{COLLECTION_NAME=$COLLECTION_NAME,OPENAI_API_KEY=$OPENAI_API_KEY,ZILLIZ_CLUSTER_ENDPOINT=$ZILLIZ_CLUSTER_ENDPOINT,ZILLIZ_CLUSTER_TOKEN=$ZILLIZ_CLUSTER_TOKEN}"