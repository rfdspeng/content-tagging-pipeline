from typing import List
from haystack import Document, component
# from copy import deepcopy
import re

@component
class MetadataCleaner:
    def __init__(self):
        self.search_filetype = re.compile(r"\.[a-zA-Z0-9]+$")

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        clean_docs = [self._clean_metadata(doc) for doc in documents]
        return {"documents": clean_docs}
    
    def _clean_metadata(self, doc: Document) -> Document:
        clean_doc = Document(
            id=doc.id,
            content=doc.content,
            embedding=doc.embedding,
            meta={"metadata": {}}
        )

        title = doc.meta.get("title") or doc.meta.get("file_path")
        file_type = self.search_filetype.search(title).group() if isinstance(title, str) else None

        clean_doc.meta["metadata"] = {
            "tags": [],
            "source_id": doc.meta.get("source_id", None),
            "title": title,
            "file_type": file_type,
            "page_number": doc.meta.get("page_number", None),
            "split_overlap_ids": [d["doc_id"] for d in doc.meta.get("_split_overlap", [])]
        }

        return clean_doc

# @component
# class MetadataCleaner:
#     @component.output_types(documents=List[Document])
#     def run(self, documents: List[Document]):
#         docs = [self._add_metadata(doc) for doc in documents]
#         return {"documents": documents}
    
#     def _add_metadata(self, doc: Document) -> Document:
#         # Initialize the new metadata dictionary
#         doc.meta["metadata"] = {
#             "tags": [],
#             "source_id": doc.meta.pop("source_id", None),
#             "file_path": doc.meta.pop("file_path", None),
#             "page_number": doc.meta.pop("page_number", None),
#             "split_overlap_ids": [d["doc_id"] for d in doc.meta.pop("_split_overlap", [])]
#         }

#         # Remove all keys except "metadata"
#         keys_to_remove = [key for key in list(doc.meta) if key != "metadata"]
#         for key in keys_to_remove:
#             doc.meta.pop(key)

#         return doc