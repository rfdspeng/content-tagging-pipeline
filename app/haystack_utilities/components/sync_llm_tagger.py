from typing import List
from haystack import Pipeline, Document, component
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator
import json

@component
class SyncLLMTagger:
    def __init__(self, prompt_template: str, temperature: float=0.2, max_tokens: int=30):
        pipe = Pipeline()
        pipe.add_component("prompt_builder", PromptBuilder(template=prompt_template))
        pipe.add_component("generator", OpenAIGenerator(generation_kwargs={"temperature": temperature, "max_tokens": max_tokens}))
        pipe.connect("prompt_builder", "generator")
        self.tag_pipe = pipe
    
    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]):
        for doc in documents:
            tags = self.tag_pipe.run({"prompt_builder": {"doc": doc}})
            doc.meta["metadata"]["tags"] = json.loads(tags["generator"]["replies"][0])
        
        return {"documents": documents}