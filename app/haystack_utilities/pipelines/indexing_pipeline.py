from haystack_utilities.components import MetadataCleaner
from haystack_utilities.components import DocumentSplitterByFunction
from haystack_utilities.tools import MilvusContextManager
from typing import List, Callable, Any
from pymilvus import MilvusClient, DataType
from haystack import Pipeline
from haystack.components.converters import PyPDFToDocument
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter, RecursiveDocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret
from milvus_haystack import MilvusDocumentStore
import nltk
from copy import deepcopy

def build_indexing_pipeline(collection_name: str, splitting_options: dict[str, Any] | Callable[[str], List[str]], file_extension: str=".pdf", embed_dim: int=768, max_content_len_chars: int=4096, drop_old: bool=False) -> Pipeline:

    if file_extension == ".pdf":
        converter = PyPDFToDocument(extraction_mode="layout")
        # converter = PyPDFToDocument()
    else:
        raise Exception(f"{file_extension} not supported in indexing pipeline.")
    
    # if isinstance(splitting_options, dict):
    #     splitter = DocumentSplitter(**splitting_options)
    # elif callable(splitting_options):
    #     splitter = DocumentSplitterByFunction(splitting_options)
    # else:
    #     raise Exception("splitting_options must be a dictionary or a callable.")

    splitting_options = deepcopy(splitting_options)
    split_strategy = splitting_options.pop("split_strategy", None)
    if split_strategy == "fixed":
        splitter = DocumentSplitter(**splitting_options)
    elif split_strategy == "recursive":
        splitter = RecursiveDocumentSplitter(**splitting_options)
    else:
        raise Exception("Valid split strategies are 'fixed' and 'recursive'.")

    # If drop_old, drop the old collection and create a new one.
    # It's best to use pymilvus to define the schema: MilvusDocumentStore.write_documents() will create a collection
    # and schema based on the documents, but it sets the primary key field to VARCHAR of length 65535 by default.
    # This is a waste of space because we're using SHA-256 to generate the IDs (haystack.Document._create_id()).
    # These are 64-character IDs.
    if drop_old:
        with MilvusContextManager() as client:
            if collection_name in client.list_collections():
                client.drop_collection(collection_name)

            client = MilvusClient(
                uri=Secret.from_env_var("ZILLIZ_CLUSTER_ENDPOINT").resolve_value(),
                token=Secret.from_env_var("ZILLIZ_CLUSTER_TOKEN").resolve_value(),
            )

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
            
            client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params,
                consistency_level="Strong",
            )

    document_store = MilvusDocumentStore(
        collection_name=collection_name,
        connection_args={
            "uri": Secret.from_env_var("ZILLIZ_CLUSTER_ENDPOINT").resolve_value(),
            "token": Secret.from_env_var("ZILLIZ_CLUSTER_TOKEN").resolve_value(),
            "secure": True
            },
    )

    pipe = Pipeline()

    pipe.add_component("converter", converter)
    pipe.add_component("cleaner", DocumentCleaner())
    pipe.add_component("splitter", splitter)
    pipe.add_component("metadata_cleaner", MetadataCleaner())
    pipe.add_component("embedder", SentenceTransformersDocumentEmbedder()) # Default: sentence-transformers/all-mpnet-base-v2
    pipe.add_component("writer", DocumentWriter(document_store=document_store))

    pipe.connect("converter", "cleaner")
    pipe.connect("cleaner", "splitter")
    pipe.connect("splitter", "embedder")
    pipe.connect("embedder", "metadata_cleaner")
    pipe.connect("metadata_cleaner", "writer")

    return pipe