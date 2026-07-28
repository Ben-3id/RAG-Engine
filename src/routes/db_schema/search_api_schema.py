from pydantic import BaseModel
from pydantic import Field

class SearchRequeset(BaseModel):
    query:str = Field(...)
    limit:int = None