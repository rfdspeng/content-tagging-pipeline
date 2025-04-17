from typing import List, Any
from haystack import Pipeline, Document, component
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
import json
from haystack_utilities.tools import TaggingKwargs

# Multi-label tagging
@component
class SyncLLMTagger:

    def __init__(self, prompt_template: str, tagging_kwargs: dict[str, Any]={}):
        tagging_kwargs = TaggingKwargs(**tagging_kwargs)

        pipe = Pipeline()
        pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template, required_variables="*"))
        pipe.add_component("generator", OpenAIGenerator(model=tagging_kwargs.model, generation_kwargs={"temperature": tagging_kwargs.temperature, "max_completion_tokens": tagging_kwargs.max_completion_tokens}))
        pipe.connect("prompt_builder", "generator")
        self.tag_pipe = pipe
        self.tag_threshold = tagging_kwargs.tag_threshold
        self.untagged_option = tagging_kwargs.untagged_option.value
    
    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        # doc_dict schema:
        # Top-level key: "source_id"
            # "tagged_docs" -> list of tagged docs
            # "untagged_docs" -> list of untagged docs
            # "tags"
                # "tag1" -> count
                # "tag2" -> count
                # etc.
        doc_dict = {}
        for doc in documents:
            source_id = doc.meta["metadata"]["source_id"]
            if source_id not in doc_dict:
                doc_dict[source_id] = {
                    "tagged_docs": [],
                    "untagged_docs": [],
                    "tags": {}
                }

            tags = self.tag_pipe.run({"prompt_builder": {"doc": doc}})

            try:
                tags = json.loads(tags["generator"]["replies"][0])
            except json.JSONDecodeError as e:
                print(f"Tagger output should be in JSON format but is instead {tags["generator"]["replies"][0]}.")
                raise e

            if not isinstance(tags, list):
                raise Exception(f"SyncLLMTagger.run(): Expected tags to be list, but got {type(tags)}.")
            elif tags == []:
                doc_dict[source_id]["untagged_docs"].append(doc)
            else:
                doc_dict[source_id]["tagged_docs"].append(doc)
                for tag in tags:
                    doc_dict[source_id]["tags"][tag] = doc_dict[source_id]["tags"].get(tag, 0) + 1
        
        for source_id in doc_dict:
            total = len(doc_dict[source_id]["tagged_docs"])
            if total > 0:
                keep_tags = [tag for tag, count in doc_dict[source_id]["tags"].items() if count/total >= self.tag_threshold]
                for doc in doc_dict[source_id]["tagged_docs"]:
                    doc.meta["metadata"]["tags"] = keep_tags
                
                if self.untagged_option == "tag":
                    for doc in doc_dict[source_id]["untagged_docs"]:
                        doc.meta["metadata"]["tags"] = keep_tags
        
        if self.untagged_option == "discard":
            documents = []
            for source_id in doc_dict:
                documents.extend(doc_dict[source_id]["tagged_docs"])

        return {"documents": documents}
    


    
# Single-label tagging
@component
class SyncSingleLabelLLMTagger:
    def __init__(self, prompt_template: str, temperature: float=0, max_tokens: int=30):
        pipe = Pipeline()
        pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
        pipe.add_component("generator", OpenAIGenerator(generation_kwargs={"temperature": temperature, "max_tokens": max_tokens}))
        pipe.connect("prompt_builder", "generator")
        self.tag_pipe = pipe
    
    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        # doc_dict schema:
        # Top-level key: "source_id"
            # "tagged_docs" -> list of tagged docs
            # "untagged_docs" -> list of untagged docs
            # "tags"
                # "tag1" -> count
                # "tag2" -> count
                # etc.
        doc_dict = {}
        for doc in documents:
            source_id = doc.meta["metadata"]["source_id"]
            if source_id not in doc_dict:
                doc_dict[source_id] = {
                    "tagged_docs": [],
                    "untagged_docs": [],
                    "tags": {}
                }

            tags = self.tag_pipe.run({"prompt_builder": {"doc": doc}})
            # doc.meta["metadata"]["tags"] = json.loads(tags["generator"]["replies"][0])
            tags = json.loads(tags["generator"]["replies"][0])

            if not isinstance(tags, list):
                raise Exception(f"SyncLLMTagger.run(): Expected tags to be list, but got {type(tags)}")
            elif tags == []:
                doc_dict[source_id]["untagged_docs"].append(doc)
            else:
                doc_dict[source_id]["tagged_docs"].append(doc)
                tag = tags[0] # For now, there should only be 1 tag
                doc_dict[source_id]["tags"][tag] = doc_dict[source_id]["tags"].get(tag, 0) + 1
        
        for source_id in doc_dict:
            total = len(doc_dict[source_id]["tagged_docs"])
            if total > 0:
                keep_tags = [tag for tag, count in doc_dict[source_id]["tags"].items() if count/total >= 0.3]
                for doc in doc_dict[source_id]["tagged_docs"]:
                    doc.meta["metadata"]["tags"] = keep_tags

        # No need to construct list from doc_dict since the documents are objects anyway
        return {"documents": documents}