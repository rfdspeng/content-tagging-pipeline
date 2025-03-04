from typing import List
from haystack import Document, component
from pymilvus import MilvusClient
from haystack.utils import Secret
    
@component
class MilvusQueryRetriever:
    def __init__(self):
        self.client = MilvusClient(
            uri=Secret.from_env_var("ZILLIZ_CLUSTER_ENDPOINT").resolve_value(),
            token=Secret.from_env_var("ZILLIZ_CLUSTER_TOKEN").resolve_value()
        )

    @component.output_types(documents=List[Document])
    def run(self, collection_name: str, ids: list[str] | None=None):
        if ids:
            # Retrieve specific IDs
            res = self.client.get(
                collection_name=collection_name,
                ids=ids,
                output_fields=["*"]
            )
        else:
            # If no IDs provided, query all entities with empty tags
            res = self.client.query(
                collection_name=collection_name,
                filter='metadata["tags"] == []',
                output_fields=["*"],
            )

        # Convert from entity format to Document format
        return {"documents": [self.dict_to_doc(d) for d in res]}
    
    def dict_to_doc(self, d: dict) -> Document:
        return Document(id=d["id"], embedding=d["vector"], content=d["text"], meta={"metadata": d["metadata"]})

