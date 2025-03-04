from typing import List
from haystack import Document, component

@component
class MetadataCleaner:
    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        docs = [self._add_metadata(doc) for doc in documents]
        return {"documents": documents}
    
    def _add_metadata(self, doc: Document) -> Document:
        # Initialize the new metadata dictionary
        doc.meta["metadata"] = {
            "tags": [],
            "source_id": doc.meta.pop("source_id", None),
            "file_path": doc.meta.pop("file_path", None),
            "page_number": doc.meta.pop("page_number", None),
            "split_overlap_ids": [d["doc_id"] for d in doc.meta.pop("_split_overlap", [])]
        }

        # Remove all keys except "metadata"
        keys_to_remove = [key for key in list(doc.meta) if key != "metadata"]
        for key in keys_to_remove:
            doc.meta.pop(key)

        return doc