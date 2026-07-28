from .base import Base_Model
from sqlalchemy.orm import Mapped , mapped_column , relationship 
from sqlalchemy.dialects.postgresql import JSONB , TSVECTOR
from sqlalchemy import ForeignKey , String , func , DateTime , Integer  , Computed , text
import uuid
from sqlalchemy import Index
from paradedb.sqlalchemy import indexing



class Chunk(Base_Model):
    __tablename__="chunks"

    chunk_id:Mapped[uuid.UUID] = mapped_column(primary_key=True ,default=uuid.uuid7)
    asset_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("assets.asset_id"))
    topic_id:Mapped[uuid.UUID] = mapped_column(ForeignKey("topics.topic_id") , nullable=False , index=True )
    
    text:Mapped[str] = mapped_column(nullable=False)

    chunk_metadata:Mapped[dict] = mapped_column(JSONB  ,
                                                nullable=False,
                                                default=dict) 

    created_at = mapped_column(DateTime(timezone=True) , server_default=func.now() , nullable=False)

    asset = relationship("Asset" ,back_populates="chunk")
    vector = relationship(  "PGVector" ,
                            back_populates="chunk" ,
                            cascade="all, delete-orphan" ,
                            uselist=False)

Index(
    "ix_chunks_topic_id",
    "topic_id"
),
Index(
    "idx_computed_text_column",
    indexing.BM25Field(Chunk.chunk_id),
    text("(text::pdb.simple('stemmer=english' , 'stopwords_language=english'))"),
    postgresql_using="bm25" ,
    postgresql_with={"key_field": "chunk_id"}
),


