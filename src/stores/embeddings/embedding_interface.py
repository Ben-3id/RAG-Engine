from abc import ABC  , abstractmethod 
from typing import List


class  EmbeddingModel(ABC):

    @abstractmethod
    def embedding_chunks(self , texts:str) -> List[float]:
        pass

    def embedding_query(self , texts:str) -> List[float]:
        pass