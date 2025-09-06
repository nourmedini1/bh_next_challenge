from pydantic import BaseModel 
from typing import List, Optional



# ===========================================
# # Request Models
# ===========================================

class UpdateAgentRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]

class CreateTagRequest(BaseModel):
    name: str

class UpdateTagRequest(BaseModel):
    name: Optional[str]


class CreateTermRequest(BaseModel):
    name: str
    description: str
    tags: List[str]
    synonyms: Optional[List[str]] = []

class UpdateTermRequest(BaseModel):
    name: Optional[str]
    description: Optional[str]
    tags: Optional[List[str]]
    synonyms: Optional[List[str]] = []

class CreateGuidelineRequest(BaseModel):
    condition: str
    action: str
    tags: List[str]
    metadata: dict

class UpdateGuidelineRequest(BaseModel):
    condition: Optional[str]
    action: Optional[str]
    tags: Optional[List[str]]
    metadata: Optional[dict]

class CreateJourneyRequest(BaseModel) : 
    title : str
    description : str
    conditions : List[str]
    tags : List[str]

class UpdateJourneyRequest(BaseModel) :
    title : Optional[str]
    description : Optional[str]
    conditions : Optional[List[str]]
    tags : Optional[List[str]]

# ===========================================
# Response Models
# ===========================================

class AgentResponse(BaseModel):
    id: str
    name: str
    description: str
    tags: List[str]

class TagResponse(BaseModel):
    id: str
    name: str

class TermResponse(BaseModel):
    id: str
    name: str
    description: str
    synonyms: List[str]
    tags: List[str]

class GuidelineResponse(BaseModel):
    id: str
    condition: str
    action: str
    tags: List[str]
    metadata: dict

class JourneyResponse(BaseModel):
    id: str
    title : str
    description : str
    conditions : List[str]
    tags : List[str]

