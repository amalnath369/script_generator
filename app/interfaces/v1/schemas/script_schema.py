from pydantic import BaseModel
from typing import List


class CreateScriptRequest(BaseModel):
    name: str
    content: str
    tags: List[str]


class ScriptResponse(BaseModel):
    id: str
    name: str
    content: str
    tags: List[str]
    status: str
    