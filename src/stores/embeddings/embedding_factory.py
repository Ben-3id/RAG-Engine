from .providers import  BAAI
from .embeddings_enum import EmbeddingEnum
from .embedding_loader import check_model_exsits , check_path
import os

class EmbeddingFactory:
    def __init__(self , config):
        self.config = config
        pass

    def create(self, provider ):
        check_path(self.config)
        check_model_exsits(self.config)
        if provider == EmbeddingEnum.BAAI.value:
            model = os.path.join(
                                self.config.LOCAL_MODELS_PATH,
                                self.config.MODEL_ID
                            )
            return BAAI(
                model
            )