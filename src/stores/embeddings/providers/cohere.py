from ..embedding_interface import EmbeddingModel
from typing import List
import cohere

class Cohere(EmbeddingModel):
    def __init__(self , api , model_id:str):
        super().__init__()
        self.api = api
        self.model_id = model_id
        self.client = cohere.AsyncClientV2(api)

    async def embedding_chunks(self , texts:List[str]) -> List[float]:
        results = await self.client.embed(
                texts=texts,
                model=self.model_id,
                input_type="search_document",
                embedding_types=["float"], 
                )

        return results.embeddings.float_

    async def embedding_query(self , texts:List[str]) -> List[float]:
        results = await self.client.embed(
                texts=texts,
                model=self.model_id,
                input_type="search_query",
                embedding_types=["float"], 
                )

        return results.embeddings.float_[0]
