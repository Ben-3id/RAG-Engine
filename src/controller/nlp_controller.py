from .base_controller import BaseController
from typing import List , Tuple
from model.database.db_schema import Chunk , PGVector
import logging 
import time
from uuid import UUID
logger = logging.getLogger("uvicorn")

class NLPController(BaseController):
    def __init__(self , embeddings_model , generate_model  , vector_model ):
        super().__init__()
        self.embeddings_model = embeddings_model
        self.generate_model = generate_model
        self.vector_model = vector_model

    async def index_into_vectordb(self , chunks:List[Tuple] , batch_size:int=1000):
        chunk_ids = []
        texts = []
        vectors = []
        objs = []

        for chunk in chunks:
            chunk_ids.append(chunk[0])
            texts.append(chunk[1])

        for i in range(0 , len(texts) , batch_size):
            results = self.embeddings_model.embedding_chunks(texts = texts[i : i + batch_size])
            vectors.extend(results)

        for vec , chunk_id in zip(vectors , chunk_ids):
            objs.append(
                PGVector(chunk_id= chunk_id,
                        embedding = vec)
                        )

        await self.vector_model.insert_many(embeddings=objs , batch_size =batch_size)
        return len(chunks)

    async def semantic_search(self , topic_id:UUID , query:List[str] , limit:int):

        start_embed = time.perf_counter()

        query = self.embeddings_model.embedding_query(query)

        end_embed = time.perf_counter()
        logger.error(f"embed query time {(end_embed - start_embed) * 1000:.2f} ms")

        start_search = time.perf_counter()
        results = await self.vector_model.search_by_topic(topic_id= topic_id , query=query , limit= limit)

        end_search = time.perf_counter()
        logger.error(f"search in vectordb time {(start_search - end_search) * 1000:.2f} ms")
        
        return results

    def rrf(self , results_lists:List[List] , K:int):

        fused = {}

        for result_list in results_lists:

            for rank , item in enumerate(result_list):

                chunk_id = item["chunk_id"]
                if chunk_id not in fused:
                    fused[chunk_id] = {
                    "chunk_id": chunk_id,
                    "text": item["text"],
                    "rrf_score": 0
                }
                fused[chunk_id]["rrf_score"] += 1 / (K + rank)

        return sorted(
        fused.values(),
        key=lambda x: x["rrf_score"],
        reverse=True
        )