from haystack import Pipeline
from milvus_haystack import MilvusDocumentStore
from haystack.utils import Secret
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
from milvus_haystack.milvus_embedding_retriever import MilvusEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder

def build_rag_pipeline(collection_name: str, prompt_template: str, top_k: int=10) -> Pipeline:

    # For the RAG prompt template, do we ask the LLM to identify which tag to filter by?
    # Is this going to be a chatbot? Should we store conversation history? You might need OpenAIChatGenerator.
    # This might be more of an AI agent.

    # Search params are passed during MilvusDocumentStore initialization

    # Initialize document store
    document_store = MilvusDocumentStore(
        collection_name=collection_name,
        connection_args={
            "uri": Secret.from_env_var("ZILLIZ_CLUSTER_ENDPOINT").resolve_value(),
            "token": Secret.from_env_var("ZILLIZ_CLUSTER_TOKEN").resolve_value(),
            "secure": True
            },
    )

    # Filters are passed during MilvusEmbeddingRetriever initialization - how can I update this dynamically?

    pipe = Pipeline()

    pipe.add_component("query_embedder", SentenceTransformersTextEmbedder()) # Default: sentence-transformers/all-mpnet-base-v2
    pipe.add_component("retriever", MilvusEmbeddingRetriever(document_store=document_store, top_k=top_k))
    pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
    pipe.add_component("generator", OpenAIGenerator(generation_kwargs={"temperature": 0.7, "max_completion_tokens": 1000})) # Update this

    pipe.connect("query_embedder", "retriever")
    pipe.connect("retriever", "prompt_builder")
    pipe.connect("prompt_builder", "generator")

    return pipe