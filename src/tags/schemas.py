import uuid 
from datetime import datetime
from typing import List
from pydantic import BaseModel


class TagModel(BaseModel):
    uid:uuid.UUID
    name:str
    created_at:datetime

# Contains a single field (name) for creating new tags, ensuring the necessary data is provided.
class TagCreateModel(BaseModel):
    name:str

# Contains a list of TagCreateModel instances (tags), used for adding multiple tags to a book.
class TagAddModel(BaseModel):
    tags:List[TagCreateModel]