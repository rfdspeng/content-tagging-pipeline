#!/bin/bash

# Exit early if any commands return non-zero
set -e

# Set environment variables
source .env # API keys and other sensitive variables
IMAGE_NAME=content-tagging-lms:v6
COLLECTION_NAME=ryan_test_collection

# <<< Optional parameters >>>

# TAGGING_MODEL=gpt-4.1-mini-2025-04-14
# TAGGING_TEMPERATURE=0.1
# TAGGING_MAX_TOKENS=40
# TAG_THRESHOLD=0.5
# UNTAGGED_OPTION=discard
# DEDUPLICATE_OPTION=skip

# Create the container
sudo docker run -d -p 9090:8080 \
    -e OPENAI_API_KEY=$OPENAI_API_KEY \
    -e COLLECTION_NAME=$COLLECTION_NAME \
    -e ZILLIZ_CLUSTER_ENDPOINT=$ZILLIZ_CLUSTER_ENDPOINT \
    -e ZILLIZ_CLUSTER_TOKEN=$ZILLIZ_CLUSTER_TOKEN \
    -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
    -e AWS_DEFAULT_REGION=$AWS_REGION \
    $IMAGE_NAME

# Give the container time to start
sleep 2

# Post JSON event to container endpoint - in the JSON file, the only parameters that matter are the bucket name and key. 
# Everything else was copied from a dummy example in AWS documentation. See https://docs.aws.amazon.com/lambda/latest/dg/with-s3.html
curl -X POST "http://localhost:9090/2015-03-31/functions/function/invocations" \
    -H "Content-Type: application/json" \
    -d @test_event.json

# Clean up container
sudo docker stop $(sudo docker ps -a -q --filter "ancestor=$IMAGE_NAME")
sudo docker rm $(sudo docker ps -a -q --filter "ancestor=$IMAGE_NAME")