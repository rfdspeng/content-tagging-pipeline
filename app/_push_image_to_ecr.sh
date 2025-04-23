#!/bin/bash
set -e

# Set environment variables
# .env must include ECR_LINK
# ECR_LINK = <account-id>.dkr.ecr.<region>.amazonaws.com
source .env
AWS_PROFILE_NAME=beamdata # If Beam Data credentials are not your default profile
IMAGE_NAME="content-tagging-lms:v7" # Local image name
ECR_REPO="content-tagging/content-tagging-lms:v7" # ECR namespace and repo name

aws ecr get-login-password --profile $AWS_PROFILE_NAME --region $AWS_REGION | sudo docker login --username AWS --password-stdin $ECR_LINK

export DOCKER_CONFIG=/root/.docker

ECR_URI="${ECR_LINK}/${ECR_REPO}"

sudo docker tag $IMAGE_NAME $ECR_URI

sudo docker push $ECR_URI