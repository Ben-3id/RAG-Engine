from .base import Base_Model
from sqlalchemy.orm import Mapped , mapped_column , relationship 

from sqlalchemy import ForeignKey , String , func , DateTime
import uuid

class Asset(Base_Model):
    __tablename__="assets"

    asset_id:Mapped[uuid.UUID] = mapped_column(primary_key=True ,default=uuid.uuid7)
    topic_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.topic_id" ,ondelete="CASCADE"))
    name:Mapped[str] = mapped_column(nullable=False)
    size:Mapped[int] = mapped_column()
    description = mapped_column(String) 
    type = mapped_column(String) 
    filehash = mapped_column(String) 

    created_at = mapped_column(DateTime(timezone=True) , server_default=func.now() , nullable=False)
    updated_at = mapped_column(DateTime(timezone=True) , onupdate=func.now() , nullable=True)
    
    topic = relationship("Topic" ,back_populates="asset")
    chunk = relationship("Chunk" ,back_populates="asset" , cascade="all, delete-orphan")
