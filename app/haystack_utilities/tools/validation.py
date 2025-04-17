from enum import Enum
from pydantic import BaseModel, confloat

class UntaggedOption(str, Enum):
    keep = 'keep'
    discard = 'discard'
    tag = 'tag'

class TaggingKwargs(BaseModel):
    model: str = 'gpt-4o-mini'
    temperature: float = 0
    max_completion_tokens: int = 30
    tag_threshold: confloat(ge=0, le=1) = 0.3
    untagged_option: UntaggedOption = UntaggedOption.keep