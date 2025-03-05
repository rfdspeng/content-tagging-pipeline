from typing import List
from haystack import Document, component
from milvus_haystack import MilvusDocumentStore
from haystack.utils import Secret
    
@component
class MilvusQueryRetriever:
    def __init__(self, document_store: MilvusDocumentStore):
        self.document_store = document_store

    @component.output_types(documents=List[Document])
    def run(self, ids: list[str] | None=None):
        if ids:
            # Retrieve specific IDs
            res = self.document_store.client.get(
                collection_name=self.document_store.collection_name,
                ids=ids,
                output_fields = ["*"]
            )
        else:
            # If no IDs provided, query all entities with empty tags
            res = self.document_store.client.query(
                collection_name=self.document_store.collection_name,
                filter='metadata["tags"] == []',
                output_fields=["*"],
            )

        # Convert from entity format to Document format
        return {"documents": [self.document_store._parse_document(d) for d in res]}

