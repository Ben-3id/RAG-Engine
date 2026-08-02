from .base import Base_Model
from sqlalchemy.orm import Mapped , mapped_column , relationship
from sqlalchemy import ForeignKey 
from sqlalchemy import UUID
from pgvector.sqlalchemy import Vector


class PGVector(Base_Model):
    __tablename__ = "embeddings"

    chunk_id = mapped_column(UUID(as_uuid=True) , ForeignKey("chunks.chunk_id") , primary_key=True)
    
    embedding = mapped_column(Vector(384) , nullable=False )

    chunk = relationship("Chunk" , back_populates="vector")
