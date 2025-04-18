from typing import List
from haystack import Document, component
from milvus_haystack import MilvusDocumentStore
from haystack.utils import Secret
from haystack_utilities.tools import DeduplicateOption, DeduplicateEnum

@component
class DuplicateChecker:
    """
    Check if the primary key (id) already exists in the vector database.
    If the primary key already exists, then either delete the entities from the vector database OR 
    do not pass the Document to the next component in the pipeline (skip the Document).
    """
    def __init__(self, document_store: MilvusDocumentStore, deduplicate_option: DeduplicateOption=DeduplicateOption()):
        self.document_store = document_store
        self.deduplicate_option = deduplicate_option.deduplicate_option

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        if not(self.deduplicate_option == DeduplicateEnum.DISABLE):
            res = self.document_store.client.get(
                collection_name=self.document_store.collection_name,
                ids=[doc.id for doc in documents],
                output_fields = ["*"]
            )

            if len(res) > 0:
                res_ids = [d[self.document_store._primary_field] for d in res]
                n_dups = len(res_ids)
                n_total = len(documents)
                
                if self.deduplicate_option == DeduplicateEnum.DELETE:
                    print(f"Found {n_dups} duplicate IDs, out of {n_total} input Documents, in the vector store. Deleting them from the database.")
                    self.document_store.delete_documents(res_ids) 
                elif self.deduplicate_option == DeduplicateEnum.SKIP:
                    documents = [doc for doc in documents if doc.id not in res_ids]
                    print(f"Found {n_dups} duplicate IDs, out of {n_total} input Documents, in the vector store. Skipping these IDs and passing {len(documents)} Documents to the next component.")
        
        return {"documents": documents}