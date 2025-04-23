#!/bin/bash

# https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html

# Exit early if any commands return non-zero
set -e

# Set environment variables
source .env
AWS_PROFILE_NAME=beamdata # If Beam Data credentials are not your default profile
ROLE_NAME=lambda-s3-trigger-role

aws iam create-role \
    --profile $AWS_PROFILE_NAME \
    --role-name $ROLE_NAME \
    --assume-role-policy-document '{"Version": "2012-10-17","Statement": [{ "Effect": "Allow", "Principal": {"Service": "lambda.amazonaws.com"}, "Action": "sts:AssumeRole"}]}'

aws iam attach-role-policy \
    --profile $AWS_PROFILE_NAME \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

aws iam attach-role-policy \
    --profile $AWS_PROFILE_NAME \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess