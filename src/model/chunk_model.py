from sqlalchemy import Insert , Select , Delete , Update , func , select , text
from .base_model import BaseModel
from .database.db_schema import Topic , Chunk , Asset
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from paradedb.sqlalchemy import pdb, search , tokenizer
import logging


logger = logging.getLogger("uvicorn")

class ChunkModel(BaseModel):
    CUSTOM_STOP_WORDS = {"what", "where", "why", "how", "is", "and", "the"}
    def __init__(self, db_client):
        self.db_client = db_client


    async def add_chunk(self,chunk:Chunk ):

        async with self.db_client as session:
            async with session.begin():
               session.add(chunk)
            await session.commit()    
            await session.refresh(chunk)
        return chunk

    async def delete_chunk_by_asset(self,asset_id: str):
                    
        async with self.db_client as session:
            async with session.begin():
                await session.execute(Delete(Chunk).where(Chunk.asset_id == asset_id))
            await session.commit()
        return True

    async def insert_many_chunks(self, chunks:List[Chunk] ,batch_size:int =100):
        async with self.db_client as session:
            async with session.begin():
                for i in range(0 , len(chunks) , batch_size):
                    session.add_all(chunks[i : i+batch_size])
            await session.commit()
        return len(chunks)

    async def get_topic_chunks(self , topic_id:UUID , last_chunk_id:int = None , batch_size:int = 1000):
        async with self.db_client as session:
            stmt =( Select(
                Chunk.chunk_id ,
                Chunk.text ,
                Chunk.topic_id
                )
                .where(Chunk.topic_id == topic_id)
                )
            
            if last_chunk_id is not None :
                stmt = stmt.where(
                    Chunk.chunk_id > last_chunk_id ,
                    )
            stmt = (
            stmt 
            .order_by(Chunk.chunk_id)
            .limit(batch_size)
            )

            results = await session.execute(stmt)
        return results.all()

    async def text_search_by_topic(self , topic_id:UUID , query:str , limit:int): #ai help

        async with self.db_client as session:

            score = func.similarity(
                Chunk.processed_text,
                query
            )

            stmt = (
                select(
                    Chunk.text,
                    Chunk.chunk_id,
                    score.label("score")
                )
                .where(
                    Chunk.processed_text.ilike(f"%{query}%"),
                    # Chunk.topic_id == topic_id
                )
                .order_by(
                    score.desc()
                )
                .limit(limit)
            )

            result = await session.execute(stmt)

        return [
            {
                "text": row.text,
                "chunk_id": row.chunk_id,
                "score": row.score
            }
            for row in result
        ]



    def clean_query(self , query: str) -> str:
        words = query.split()
        filtered = [w for w in words if w.ؤlower() not in ChunkModel.CUSTOM_STOP_WORDS]
        return " ".join(filtered)

    def make_prefix_query(self , query:str):
        splited_query = query.split()
        return " & ".join(
            f"{word}:*"
            for word in splited_query
        )