import lambda_function
import os
# print(lambda_function.s3)
# bucket = lambda_function.s3.Bucket("content-tagging-lms")
# for o in bucket.objects.limit(10):
#     print(o.key)

import urllib.parse

# os.environ["TAGGING_MODEL"] = "gpt-4.1-mini-2025-04-14"
# os.environ["TAGGING_TEMPERATURE"] = "0.1"
# os.environ["TAGGING_MAX_TOKENS"] = "40"
# os.environ["TAG_THRESHOLD"] = "0.5"
# os.environ["UNTAGGED_OPTION"] = "discard"


# tagging_kwargs = {
#         "model": os.environ.get("TAGGING_MODEL", "gpt-4o-mini"),
#         "temperature": float(os.environ.get("TAGGING_TEMPERATURE", 0)),
#         "max_completion_tokens": int(os.environ.get("TAGGING_MAX_TOKENS", 30)),
#         "tag_threshold": float(os.environ.get("TAG_THRESHOLD", 0.3)),
#         "untagged_option": os.environ.get("UNTAGGED_OPTION", "keep"),
#     }
# tagging_kwargs = {
#     "model": "gpt-4.1-mini-2025-04-14",
#     "untagged_option": "discard",
#     "temperature": "0.1",
#     "max_completion_tokens": "40",
#     "tag_threshold": "0.5",
# }

key = 'Content/Data wrangling with Python/Class 7 - Advanced Pandas_Solutions.ipynb'
# encoded = urllib.parse.quote_plus(key, encoding='utf-8')
# print(encoded)
# print(urllib.parse.unquote_plus(encoded, encoding='utf-8'))

event = {
  "Records": [
    {
      "eventVersion": "2.1",
      "eventSource": "aws:s3",
      "awsRegion": "us-east-2",
      "eventTime": "2019-09-03T19:37:27.192Z",
      "eventName": "ObjectCreated:Put",
      "userIdentity": {
        "principalId": "AWS:AIDAINPONIXQXHT3IKHL2"
      },
      "requestParameters": {
        "sourceIPAddress": "205.255.255.255"
      },
      "responseElements": {
        "x-amz-request-id": "D82B88E5F771F645",
        "x-amz-id-2": "vlR7PnpV2Ce81l0PRw6jlUpck7Jo5ZsQjryTjKlc5aLWGVHPZLj5NeC6qMa0emYBDXOo6QBU0Wo="
      },
      "s3": {
        "s3SchemaVersion": "1.0",
        "configurationId": "828aa6fc-f7b5-4305-8584-487c791949c1",
        "bucket": {
          "name": "content-tagging-lms",
          "ownerIdentity": {
            "principalId": "A3I5XTEXAMAI3E"
          },
          "arn": "arn:aws:s3:::lambda-artifacts-deafc19498e3f2df"
        },
        "object": {
          "key": urllib.parse.quote_plus(key, encoding='utf-8'),
          "size": 1305107,
          "eTag": "b21b84d653bb07b05b1e6b33684dc11b",
          "sequencer": "0C0F6F405D6ED209E1"
        }
      }
    }
  ]
}

returned = lambda_function.lambda_handler(event, "")
print(returned)