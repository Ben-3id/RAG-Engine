from sentence_transformers import SentenceTransformer
from ..embedding_interface import EmbeddingModel
from typing import List
from pathlib import Path

class BAAI(EmbeddingModel):
    def __init__(self , embed_model):

        self.model = SentenceTransformer(fr"stores\embeddings\providers\local\{embed_model}" ,
        device="cuda" )
        self.model.encode(["warm up"] )

    def embedding_chunks(self , texts:str) -> List[float]:
        result = self.model.encode(texts)
        return result['dense_vecs']
    
    def embedding_query(self , texts:str) -> List[float]:
        result = self.model.encode(texts)
        return result['dense_vecs'][0]