from settings import  get_settings
from sqlalchemy.ext.asyncio import AsyncSession

class BaseModel:
    def __init__(self , db_client:AsyncSession):
        self.db_client = db_client
        self.settings = get_settings()