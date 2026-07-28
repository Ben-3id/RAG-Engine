from .base_model import BaseModel
from sqlalchemy import text as sql_text 
from sqlalchemy import Delete  , Select , literal
from sqlalchemy.dialects.postgresql import insert
from typing import List
from uuid import UUID
from .database.db_schema import PGVector , Chunk

class PGVectorModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)

    async def hnsw_index(self):
        async with self.db_client as session:
            async with session.begin():
                await session.execute(sql_text(
                    "CREATE INDEX IF NOT EXISTS embeddings_embedding_hnsw_idx "
                    "ON embeddings "
                    "USING hnsw (embedding vector_cosine_ops); "
                ))
            await session.commit()
        return True

    async def insert_many(self , embeddings:List[PGVector] , batch_size:int):
        async with self.db_client as session:
            async with session.begin():
                for i  in range(0 , len(embeddings) , batch_size):
                    batch = embeddings[i : i + batch_size]
                    stmt = insert(PGVector).values(
                        [
                            {
                        "chunk_id" : obj.chunk_id ,
                        "embedding" : obj.embedding
                        }
                     for obj in batch
                    ] )

                    stmt= stmt.on_conflict_do_nothing(index_elements=["chunk_id"])
                    await session.execute(stmt)

        return len(embeddings)


    async def delete_embedding_by_asset_id(self, Chunk_id: str):
                    
        async with self.db_client as session:
            async with session.begin():
                await session.execute(Delete(PGVector).where(PGVector.Chunk_id == Chunk_id))
            await session.commit()
        return True

    async def search_by_topic(self , topic_id:UUID , query:List[float] , limit:int = 5):

        async with self.db_client as session:
            score = (
                literal(1) - PGVector.embedding.cosine_distance(query)
            ).label("similarity")

            stmt = (Select(Chunk.text , score , Chunk.chunk_id)
                    .join(PGVector.chunk)
                    # .where(Chunk.topic_id == topic_id)
                    .order_by(score.desc())
                    .limit(limit= limit))

            result = await session.execute(stmt)
            return [
            {
                "text": row[0],
                "score": float(row[1]),
                "chunk_id":row[2]
            }
            for row in result.all()
        ]