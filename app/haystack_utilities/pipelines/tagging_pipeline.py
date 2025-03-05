from haystack_utilities.components import MilvusQueryRetriever
from haystack_utilities.components import SyncLLMTagger
from haystack_utilities.components import DocumentUpserter
from haystack import Pipeline
from milvus_haystack import MilvusDocumentStore
from haystack.utils import Secret

def build_tagging_pipeline(collection_name: str, prompt_template: str) -> Pipeline:

    # Initialize document store
    document_store = MilvusDocumentStore(
        collection_name=collection_name,
        connection_args={
            "uri": Secret.from_env_var("ZILLIZ_CLUSTER_ENDPOINT").resolve_value(),
            "token": Secret.from_env_var("ZILLIZ_CLUSTER_TOKEN").resolve_value(),
            "secure": True
            },
    )

    pipe = Pipeline()

    pipe.add_component("queryer", MilvusQueryRetriever(document_store))
    pipe.add_component("tagger", SyncLLMTagger(prompt_template))
    pipe.add_component("upserter", DocumentUpserter(document_store=document_store))
    
    pipe.connect("queryer", "tagger")
    pipe.connect("tagger", "upserter")

    return pipe