#!/bin/bash

# Exit early if any commands return non-zero
set -e

# Set environment variables
source .env
AWS_PROFILE_NAME=beamdata # If Beam Data credentials are not your default profile
BUCKET_NAME=content-tagging-lms-lambda-v7

aws s3 mb --profile $AWS_PROFILE_NAME "s3://${BUCKET_NAME}"