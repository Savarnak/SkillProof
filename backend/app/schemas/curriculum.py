from pydantic import BaseModel, Field
from typing import List, Optional

class Topic(BaseModel):
    topic_id: str
    name: str
    description: str
    learning_objectives: List[str] = Field(default_factory=list)
    key_tools: List[str] = Field(default_factory=list)

class CurriculumDay(BaseModel):
    day_number: int
    day_id: str
    title: str
    topics: List[Topic] = Field(default_factory=list)

class Module(BaseModel):
    module_id: str
    title: str
    days: List[CurriculumDay] = Field(default_factory=list)

class Curriculum(BaseModel):
    curriculum_id: str
    title: str
    description: str
    version: str = "1.0.0"
    modules: List[Module] = Field(default_factory=list)
