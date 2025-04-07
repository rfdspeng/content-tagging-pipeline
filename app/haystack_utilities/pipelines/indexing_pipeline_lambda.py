from haystack_utilities.components import MetadataCleaner, JupyterNotebookConverter, SyncLLMTagger
from haystack_utilities.tools import MilvusContextManager
from haystack_utilities.ml import tagging_prompt, tagging_prompt_ipynb
from typing import List, Callable, Any
from pymilvus import MilvusClient, DataType
from haystack import Pipeline
from haystack.components.routers import FileTypeRouter, MetadataRouter
from haystack.components.converters import PyPDFToDocument, TextFileToDocument, PPTXToDocument, HTMLToDocument
from haystack.components.joiners.document_joiner import DocumentJoiner
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter, RecursiveDocumentSplitter
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.utils import Secret
from milvus_haystack import MilvusDocumentStore
import nltk
from copy import deepcopy

def build_indexing_pipeline(collection_name: str, splitting_options: dict[str, Any] | Callable[[str], List[str]], skip_cleaner: bool=True, add_tagger: bool=False, embed_dim: int=768, max_content_len_chars: int=4096, drop_old: bool=False) -> Pipeline:

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


    """
    Create the pipeline

    File type router -> document joiner -> converters -> cleaner (optional) -> 
    Splitter -> SentenceTransformer embedder -> metadata cleaner (normalization) -> 
    Tagger (optional) -> document writer (to vector store)

    Cleaner is optional because it removes formatting, which is not desirable for human readability and may not be desirable for generation in RAG
    
    """

    pipe = Pipeline()

    # Default mime types can be found in Python mimetypes library
    # text/markdown is added by Haystack (file_type_router.py)
    # Jupyter notebooks: https://docs.jupyter.org/en/latest/reference/mimetype.html
    
    # mime_types are compiled into regular expression objects. mime_types map to file extensions.
    # Each file name passed to router is mapped to a mime type
    # The mime type of the file is matched (re.fullmatch) against mime_types, starting from the beginning of the list (which means the list order matters)
    mime_types = ["application/pdf", r"text/.*", "application/vnd.openxmlformats-officedocument.presentationml.presentation", r"application/x-ipynb\+json"]
    additional_mimetypes = {
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
        "application/x-ipynb+json": ".ipynb"
        }
    # The output of the router is a dictionary of lists. Each key is a mime type and each value is a list of file names corresponding to the mime type.
    pipe.add_component("file_type_router", FileTypeRouter(mime_types=mime_types, additional_mimetypes=additional_mimetypes))

    pipe.add_component("txt_converter", TextFileToDocument()) # For now, .txt, .md, .html, and .vtt will be routed to here
    pipe.add_component("pdf_converter", PyPDFToDocument(extraction_mode="layout"))
    pipe.add_component("pptx_converter", PPTXToDocument())
    pipe.add_component("ipynb_converter", JupyterNotebookConverter())

    pipe.add_component("converter_document_joiner", DocumentJoiner())

    if not skip_cleaner:
        pipe.add_component("cleaner", DocumentCleaner())


    """ Splitting """
    
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
    
    pipe.add_component("splitter", splitter)


    """ Normalizing metadata, embedding, tagging (optional), and writing """

    pipe.add_component("metadata_cleaner", MetadataCleaner())
    pipe.add_component("embedder", SentenceTransformersDocumentEmbedder()) # Default: sentence-transformers/all-mpnet-base-v2

    if add_tagger:
        # Jupyter notebooks will go to "ipynb_tagger" (metadata_router.ipynb)
        # All others will go to "tagger" (metadata_router.unmatched)
        rules = {
            "ipynb": {"field": "meta.metadata.file_type", 
                   "operator": "==",
                   "value": ".ipynb"
                   }
        }
        pipe.add_component("metadata_router", MetadataRouter(rules=rules))
        pipe.add_component("tagger", SyncLLMTagger(tagging_prompt))
        pipe.add_component("ipynb_tagger", SyncLLMTagger(tagging_prompt_ipynb))
        pipe.add_component("tagger_document_joiner", DocumentJoiner())

    pipe.add_component("writer", DocumentWriter(document_store=document_store))


    """ Connect components """

    # Routing to correct converter
    pipe.connect("file_type_router.text/.*", "txt_converter")
    pipe.connect("file_type_router.application/pdf", "pdf_converter")
    pipe.connect("file_type_router.application/vnd.openxmlformats-officedocument.presentationml.presentation", "pptx_converter")
    pipe.connect("file_type_router.application/x-ipynb\\+json", "ipynb_converter")

    # Joining converter outputs
    pipe.connect("txt_converter", "converter_document_joiner")
    pipe.connect("pdf_converter", "converter_document_joiner")
    pipe.connect("pptx_converter", "converter_document_joiner")
    pipe.connect("ipynb_converter", "converter_document_joiner")

    # Cleaner (optional), splitter, embedder, normalize metadata
    if not skip_cleaner:
        pipe.connect("converter_document_joiner", "cleaner")
        pipe.connect("cleaner", "splitter")
    else:
        pipe.connect("converter_document_joiner", "splitter")
        
    pipe.connect("splitter", "embedder")
    pipe.connect("embedder", "metadata_cleaner")

    # Tagger
    if add_tagger:
        pipe.connect("metadata_cleaner", "metadata_router")
        pipe.connect("metadata_router.ipynb", "ipynb_tagger")
        pipe.connect("metadata_router.unmatched", "tagger")
        pipe.connect("ipynb_tagger", "tagger_document_joiner")
        pipe.connect("tagger", "tagger_document_joiner")
        pipe.connect("tagger_document_joiner", "writer")
    else:
        pipe.connect("metadata_cleaner", "writer")

    return pipe