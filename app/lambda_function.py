# Original code: https://docs.aws.amazon.com/lambda/latest/dg/with-s3-example.html

import os
import json
import urllib.parse
import uuid
import boto3
from pathlib import Path
from haystack.components.routers import FileTypeRouter
from haystack_utilities.pipelines import indexing_pipeline_lambda
import haystack_utilities.tools
import nltk
from sentence_transformers import SentenceTransformer

# Function to load/check environment variables
def load_env_vars():
    print("Loading environment variables.")

    if not(os.environ.get("OPENAI_API_KEY")):
        raise Exception("Please provide an OPENAI_API_KEY environment variable.")

    if not(os.environ.get("ZILLIZ_CLUSTER_ENDPOINT")):
        raise Exception("Please provide a ZILLIZ_CLUSTER_ENDPOINT environment variable (uri of your Zilliz cluster).")

    if not(os.environ.get("ZILLIZ_CLUSTER_TOKEN")):
        raise Exception("Please provide a ZILLIZ_CLUSTER_TOKEN environment variable.")

    if not(collection_name := os.environ.get("COLLECTION_NAME")):
        raise Exception("Please provide a str COLLECTION_NAME environment variable. This is the name of your Zilliz collection.")

    splitting_options = os.environ.get("SPLITTING_OPTIONS", None)
    if not splitting_options:
        # sentence-transformers/all-mpnet-base-v2
        # Max tokens = 384
        # Roughly 288 words (3 words = 4 tokens)
        splitting_options = {
            "split_strategy": "fixed",
            "split_by": "word",
            "split_length": 250,
            "split_overlap": 50,
            "split_threshold": 30,
            "respect_sentence_boundary": True
        }
    else:
        try:
            splitting_options = json.loads(splitting_options)
        except json.JSONDecodeError as e:
            print("Please provide SPLITTING_OPTIONS environment variable in valid JSON format. This defines the chunking strategy.")
            raise e

    skip_cleaner = os.environ.get("SKIP_CLEANER", "True").lower() == "true"
    add_tagger = os.environ.get("ADD_TAGGER", "True").lower() == "true"

    tagging_kwargs = {
        "model": os.environ.get("TAGGING_MODEL", "gpt-4o-mini"),
        "temperature": float(os.environ.get("TAGGING_TEMPERATURE", 0)),
        "max_completion_tokens": int(os.environ.get("TAGGING_MAX_TOKENS", 30)),
        "tag_threshold": float(os.environ.get("TAG_THRESHOLD", 0.3)),
        "untagged_option": os.environ.get("UNTAGGED_OPTION", "keep"),
    }
    try:
        tagging_kwargs = haystack_utilities.tools.TaggingKwargs(**tagging_kwargs).model_dump()
    except Exception as e:
        raise e
    
    try:
        max_content_len_chars = int(os.environ.get("MAX_CHUNK_LENGTH_IN_CHARS", 65535))
    except Exception as e:
        print("MAX_CHUNK_LENGTH_IN_CHARS must be a positive integer.")
        raise e

    env_vars = {
        "collection_name": collection_name,
        "splitting_options": splitting_options,
        "skip_cleaner": skip_cleaner,
        "add_tagger": add_tagger,
        "max_content_len_chars": max_content_len_chars,
        "tagging_kwargs": tagging_kwargs,
    }

    print(f"Loaded environment variables: {env_vars}")
    return env_vars



# Set up the environment
os.environ["SENTENCE_TRANSFORMERS_HOME"] = "/tmp/" # Cache directory
env_vars = load_env_vars() # Load env vars
SentenceTransformer("sentence-transformers/all-mpnet-base-v2") # Cache embedding model
haystack_utilities.tools.create_collection(env_vars["collection_name"], max_content_len_chars=env_vars["max_content_len_chars"]) # Create collection if it doesn't exist (this is idempotent code)
file_type_router = FileTypeRouter(mime_types=haystack_utilities.tools.mime_types, additional_mimetypes=haystack_utilities.tools.additional_mimetypes) # For early termination if unsupported file type
s3 = boto3.resource("s3") # Can this connection be purged?
nltk.data.path.append("/var/task/nltk_data") # Downloaded during Docker image creation

print("Loading function.")
def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # For now, the function is only expected to process one file at a time (typical S3 -> Lambda pipeline), so there is only one Record
    # Update later if batch processing is desired
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    
    # Check that key is a valid file type
    if "unclassified" in file_type_router.run(sources=[Path(key)]).keys():
        raise Exception(f"{key} is not a supported MIME type. Supported MIME types are {haystack_utilities.tools.mime_types}")
    
    # Download the file
    bucket = s3.Bucket(bucket_name)
    try:
        file_name = Path(f"/tmp/{uuid.uuid4()}/{Path(key).name}")
        file_name.parent.mkdir()
        bucket.download_file(key, file_name)
        print(f"Downloaded object {key} from bucket {bucket_name} into {file_name.as_posix()}.")
    except Exception as e:
        print(f"Error getting object {key} from bucket {bucket_name}. Make sure they exist and your bucket is in the same region as this function.")
        raise e
    
    # Create indexing pipeline
    # (In the lambda_handler to make sure the Zilliz/OpenAI connections are always active. Move this outside of lambda_handler if you can set keep-alive directive.)
    try:
        index_pipe = indexing_pipeline_lambda.build_indexing_pipeline(env_vars["collection_name"], 
                                                              env_vars["splitting_options"], 
                                                              skip_cleaner=env_vars["skip_cleaner"], 
                                                              add_tagger=env_vars["add_tagger"],
                                                              tagging_kwargs=env_vars["tagging_kwargs"])
        print("Created indexing pipeline.")
    except Exception as e:
        print(f"Failed to create indexing pipeline.")
        raise e
    
    # Run indexing pipeline
    try:
        index_results = index_pipe.run({"file_type_router": {"sources": [file_name]}})
        print(f"Completed indexing job for {key}. {index_results["writer"]["documents_written"]} documents written to Zilliz cluster.")
    except Exception as e:
        print(f"Error encountered during indexing.")
        raise e
    
    # Delete the file
    try:
        file_name.unlink()
        file_name.parent.rmdir()
        print(f"Deleted {file_name.as_posix()}.")
    except Exception as e:
        print(e)
        print(f"Error deleting directory and file {file_name.as_posix()}")

    return index_results