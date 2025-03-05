from haystack import component, Document
from haystack.components.preprocessors import DocumentSplitter
from typing import List, Callable

@component
class DocumentSplitterByFunction:
    def __init__(self, splitting_function: Callable[[str], List[str]], split_overlap: bool=True):
        self.splitter = DocumentSplitter(split_by="function", splitting_function=splitting_function)
        self.split_overlap = split_overlap

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        split_documents: List[Document] = []

        for doc in documents:
            split_docs = self.splitter.run([doc])
            split_docs = split_docs["documents"]
            ids = [d.id for d in split_docs]

            # Get split overlaps
            if self.split_overlap and len(ids) > 1:
                if len(ids) > 1:
                    # split_overlap_ids = [[ids[1]]] + [[ids[idx-1], ids[idx+1]] for idx in range(1, len(ids)-1)] + [[ids[len(ids)-2]]]
                    split_overlap_ids = [[ids[idx-1], ids[idx+1]] for idx in range(1, len(ids)-1)]
                    split_overlap_ids.insert(0, [ids[1]])
                    split_overlap_ids.extend([[ids[len(ids)-2]]])
                else:
                    split_overlap_ids = [[]]
                
                assert len(split_overlap_ids) == len(split_docs)
                
                for idx, split_doc in enumerate(split_docs):
                    split_doc.meta["_split_overlap"] = [{"doc_id": id} for id in split_overlap_ids[idx]]
            
            split_documents += split_docs

        return {"documents": split_documents}