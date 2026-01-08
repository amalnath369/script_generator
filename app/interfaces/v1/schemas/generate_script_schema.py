from pydantic import BaseModel
from typing import List



class CreateGeneratedScriptRequest(BaseModel):
    script_id: str
    name: str
    content: str
    tags: List[str]


    
class GeneratedScriptResponse(BaseModel):
    id: str
    script_id: str
    name: str
    content: str
    tags: List[str]
    status: str

    model_config = {
        "from_attributes": True
    }


