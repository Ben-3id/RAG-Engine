from .providers import Cohere , BAAI
from .embeddings_enum import EmbeddingEnum

class EmbeddingFactory:
    def __init__(self , config):
        self.config = config
        pass

    def create(self, provider ):
        if provider == EmbeddingEnum.COHERE.value:
            return Cohere(  self.config.COHERE_API,
                            self.config.COHERE_EMBED_MODEL_ID)
        elif provider == EmbeddingEnum.BAAI.value:
            return BAAI(self.config.LOCAL_MODEL_PATH)