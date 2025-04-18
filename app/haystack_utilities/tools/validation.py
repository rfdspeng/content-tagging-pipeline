from enum import Enum
from pydantic import BaseModel, confloat

class UntaggedOption(str, Enum):
    KEEP = 'keep'
    DISCARD = 'discard'
    TAG = 'tag'

class TaggingKwargs(BaseModel):
    model: str = 'gpt-4o-mini'
    temperature: float = 0
    max_completion_tokens: int = 30
    tag_threshold: confloat(ge=0, le=1) = 0.3
    untagged_option: UntaggedOption = UntaggedOption.KEEP

class DeduplicateEnum(str, Enum):
    SKIP = 'skip'
    DELETE = 'delete'
    DISABLE = 'disable'

class DeduplicateOption(BaseModel):
    deduplicate_option: DeduplicateEnum = DeduplicateEnum.SKIP