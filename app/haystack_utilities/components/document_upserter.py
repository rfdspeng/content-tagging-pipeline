from typing import List, Optional
from haystack import Document, component
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy

@component
class DocumentUpserter(DocumentWriter):
    
    @component.output_types(documents_written=int)
    def run(self, documents: List[Document], policy: Optional[DuplicatePolicy] = None):
        """
        Run the DocumentUpserter on the given input data.

        :param documents:
            A list of documents to upsert to the document store.
        :param policy:
            The policy to use when encountering duplicate documents.
            For MilvusDocumentStore, there is no policy - duplicate IDs are inserted into the vector database so there will be multiple entities with the same ID.
        :returns:
            Number of documents written to the document store.

        :raises ValueError:
            If the specified document store is not found.
        """

        document_ids = [doc.id for doc in documents]
        self.document_store.delete_documents(document_ids)

        return_value = super(DocumentUpserter, self).run(documents, policy)
        return return_value