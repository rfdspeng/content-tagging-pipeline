from contextlib import contextmanager
from pymilvus import MilvusClient
from haystack.utils import Secret

# MilvusClient context manager
@contextmanager
def MilvusContextManager():
    client = MilvusClient(
            uri=Secret.from_env_var("ZILLIZ_CLUSTER_ENDPOINT").resolve_value(),
            token=Secret.from_env_var("ZILLIZ_CLUSTER_TOKEN").resolve_value(),
    )
    
    try:
        yield client
    finally:
        client.close()