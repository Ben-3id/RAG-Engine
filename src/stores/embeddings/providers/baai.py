from FlagEmbedding import BGEM3FlagModel
from ..embedding_interface import EmbeddingModel
from typing import List
from pathlib import Path

class BAAI(EmbeddingModel):
    def __init__(self , embed_model):
        self.model = BGEM3FlagModel(r"stores\embeddings\providers\local\bge_m3" ,
        use_fp16=True , 
        normalize_embedding=True ,
        devices="cuda" )
        self.model.encode(["warm up"])

    def embedding_chunks(self , texts:str) -> List[float]:
        result = self.model.encode_corpus(texts)
        return result['dense_vecs']
    
    def embedding_query(self , texts:str) -> List[float]:
        result = self.model.encode_queries(texts)
        return result['dense_vecs'][0]