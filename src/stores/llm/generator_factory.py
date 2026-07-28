from .providers import Gemini
from  settings import settings
from .generator_enum import GeneratorEnums
class GeneratorFactory:

    def __init__(self ,  config:settings):
        self.config = config

    def create(self , provider:str):
        if provider == GeneratorEnums.GEMINI.value:
            return Gemini(  api= self.config.GEMINI_API ,
                            model_id= self.config.GEMINI_LLM_MODEL_ID,
                            streaming= self.config.LLM_STREAM_MODE ,
                            system_instruction= None)