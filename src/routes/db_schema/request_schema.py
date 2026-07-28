from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class ProcessRequest(BaseModel):
    file_name: str =None
    asset_id: UUID = None
    topic_id: UUID = None
    batch_size :Optional[int] = 50
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0