from contextlib import contextmanager
from pymilvus import MilvusClient, DataType
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

def create_collection(collection_name: str, embed_dim: int=768, max_content_len_chars: int=4096):
    # It's best to use pymilvus to define the schema: MilvusDocumentStore.write_documents() will create a collection
    # and schema based on the documents, but it sets the primary key field to VARCHAR of length 65535 by default.
    # This is a waste of space because we're using SHA-256 to generate the IDs (haystack.Document._create_id()).
    # These are 64-character IDs.

    # Default embedding dimension is 768 because default SentenceTransformers is sentence-transformers/all-mpnet-base-v2.
    # Maximum text chunk length in characters by default is 4096, but this may not be enough for some file formats.

    with MilvusContextManager() as client:
        if collection_name in client.list_collections():
            print(f"{collection_name} already exists. Did not create a new collection.")
            return
        
        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=True,
        )

        schema.add_field(field_name="id", datatype=DataType.VARCHAR, is_primary=True, auto_id=False, max_length=64) # SHA-256
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=embed_dim)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=max_content_len_chars)
        schema.add_field(field_name="metadata", datatype=DataType.JSON)

        index_params = client.prepare_index_params()

        index_params.add_index(
            field_name="vector",
            metric_type="COSINE", # sentence-transformers/all-mpnet-base-v2 embeddings are L2-normalized
            index_type="AUTOINDEX",
            index_name="vector",
        )
        
        try:
            client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params,
                consistency_level="Strong",
            )
            print(f"Created a new collection {collection_name}.")
        except Exception as e:
            raise e