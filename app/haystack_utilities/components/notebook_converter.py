from typing import Any, Optional, List, Union, Dict
from pathlib import Path
from haystack import Document, component
from haystack.components.converters import TextFileToDocument
from haystack.dataclasses import ByteStream
import json
import re
from bs4 import BeautifulSoup

@component
class JupyterNotebookConverter(TextFileToDocument):
    def __init__(self, encoding: str = "utf-8", store_full_path: bool = False):
        super(JupyterNotebookConverter, self).__init__(encoding, store_full_path)
        self.remove_pattern = re.compile(r'!\[.*?\]\(.*?\)', flags=re.DOTALL) # remove Markdown images

    @component.output_types(documents=List[Document])
    def run(
        self,
        sources: List[Union[str, Path, ByteStream]],
        meta: Optional[Union[Dict[str, Any], List[Dict[str, Any]]]] = None,
    ):
        documents = super(JupyterNotebookConverter, self).run(sources=sources, meta=meta)["documents"]
        for doc in documents:
            doc.content = self.parse_notebook(doc.content)

        return {"documents": documents}

    def parse_notebook(self, rawtext: str) -> str:
        data = json.loads(rawtext)

        kernelspec = data.get("metadata", {}).get("kernelspec", {})
        lang = kernelspec.get("language") or kernelspec.get("name") or kernelspec.get("display_name") or ""

        all_cells = []
        for cell in data["cells"]:
            content = "".join(cell.get("source", [])).strip()
            if content == "": # ignore the cell if it's entirely whitespace (empty)
                continue

            if cell["cell_type"] == "code":
                composed_str = f"\n```{lang}\n{content}\n```\n"
            elif cell["cell_type"] == "markdown":
                content = self.remove_pattern.sub("", content) # clean up using regex
                # Remove HTML images
                content = BeautifulSoup(content, "html.parser")
                for match in content.find_all(["img"]):
                    match.decompose()
                content = str(content)
                composed_str = f"  \n{content}  \n"
            else:
                composed_str = f"  \n{content}  \n"

            all_cells.append(composed_str)

        return "".join(all_cells)