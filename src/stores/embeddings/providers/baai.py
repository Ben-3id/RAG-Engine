from sentence_transformers import SentenceTransformer
from ..embedding_interface import EmbeddingModel
from typing import List
from pathlib import Path

class BAAI(EmbeddingModel):
    def __init__(self , embed_model):

        self.model = SentenceTransformer(embed_model)
        self.model.encode(["warm up"] )

    def embedding_chunks(self , texts:str) -> List[float]:
        result = self.model.encode(texts)
        return result
    
    def embedding_query(self , texts:str) -> List[float]:
        result = self.model.encode(texts)
        return result[0]