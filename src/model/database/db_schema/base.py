from sqlalchemy.orm import DeclarativeBase
from settings import get_settings

class Base_Model(DeclarativeBase):
    config = get_settings()