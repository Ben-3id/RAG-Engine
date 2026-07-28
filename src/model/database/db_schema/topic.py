from sqlalchemy.orm import Mapped , mapped_column , relationship 
from sqlalchemy import String  , DateTime , func
from .base import Base_Model
import uuid 


class Topic(Base_Model):
    __tablename__="topics"


    topic_id:Mapped[uuid.UUID] = mapped_column(primary_key=True , default=uuid.uuid7, unique=True , nullable=False)
    topic_name:Mapped[str] = mapped_column( nullable=False , unique=True ,index=True)
    topic_description = mapped_column(String) 

    created_at = mapped_column(DateTime(timezone=True) , server_default=func.now() , nullable=False)
    updated_at = mapped_column(DateTime(timezone=True) , onupdate=func.now() , nullable=True)
    
    asset = relationship("Asset" ,back_populates="topic" ,cascade="all, delete-orphan")