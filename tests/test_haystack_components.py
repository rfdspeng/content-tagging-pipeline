from app.haystack_utilities.components import MetadataCleaner
from haystack import Document

def test_metadata_cleaner():
    # Non-metadata attributes should carry over directly
    # Metadata should be moved from doc.meta to doc.meta["metadata"]
    # Output metadata needs to include tags, source_id, file_path, page_number, and split_overlap_ids (and only these keys)
    # Use this test to enforce the correct output Document formats

    # id, content, embedding, meta

    doc1 = Document(id="king_james", 
                    content="Lebron James is the career points leader in the NBA.", 
                    meta={}, 
                    embedding=[0.1, 0.1]
                    )
    
    doc2 = Document(id="night_night", 
                    content="Stephen Curry is the only player in NBA history to be unanimously voted as the regular season MVP.", 
                    meta={
                        "source_id": "abc",
                        "file_path": "abc.pdf",
                        "page_number": 123,
                        "_split_overlap": [
                            {"doc_id": "aaa"},
                            {"doc_id": "bbb"}
                        ]
                        },
                    embedding=[0.1, 0.1]
                    )
    
    doc3 = Document(id="slim_reaper", 
                    content="Kevin Durant won two NBA Finals MVPs with the Golden State Warriors in 2017 and 2018.", 
                    meta={
                        "source_id": "abc",
                        "file_path": "abc.pdf",
                        "page_number": 123,
                        "_split_overlap": [
                            {"doc_id": "aaa"},
                            {"doc_id": "bbb"}
                        ],
                        "random_key": "random junk"
                        },
                    embedding=[0.1, 0.1]
                    )
    
    output_meta_keys = ["tags", "source_id", "file_path", "page_number", "split_overlap_ids"]
    
    documents = [doc1, doc2, doc3]
    cleaner = MetadataCleaner()
    clean_documents = cleaner.run(documents)
    clean_documents = clean_documents["documents"]

    documents = [doc1, doc2, doc3]
    assert len(documents) == len(clean_documents)
    for idx in range(len(documents)):
        doc = documents[idx]
        clean_doc = clean_documents[idx]

        assert doc.id == clean_doc.id
        assert doc.content == clean_doc.content
        assert doc.embedding == clean_doc.embedding

        for key in output_meta_keys:
            assert key in clean_doc.meta["metadata"].keys()

            if key == "split_overlap_ids":
                if "_split_overlap" in doc.meta:
                    assert [d["doc_id"] for d in doc.meta["_split_overlap"]] == clean_doc.meta["metadata"][key]
                else:
                    assert doc.meta["metadata"][key] == []
            elif key == "tags":
                assert clean_doc.meta["metadata"][key] == []
            else:
                if key in doc.meta:
                    assert doc.meta[key] == clean_doc.meta["metadata"][key]
                else:
                    assert clean_doc.meta["metadata"][key] == None