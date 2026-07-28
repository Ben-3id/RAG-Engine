from pydantic_settings import BaseSettings , SettingsConfigDict


class settings(BaseSettings):
    ''' settings class Only Use for hints \n
                             it Use get_settings func'''


    
    POSTGRES_USERNAME:str = None
    POSTGRES_PASSWORD:str = None
    DB_NAME:str = None
    FILE_SIZE:int = None
    FILE_TYPES:list = None
    LEN_UNIQUE_STR:int = None
    HASH_ALGORITHM:str = None

    VECTOR_LENGTH:int = None

    EMBED_PROVIDER:str = None
    COHERE_EMBED_MODEL_ID:str = None
    COHERE_API:str =None
    LOCAL_MODEL_PATH:str = None
    
    LLM_PROVIDER:str = None
    GEMINI_API:str = None
    GEMINI_LLM_MODEL_ID:str =None
    LLM_STREAM_MODE:bool = None


    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8" ,extra="ignore")


def get_settings() -> settings:
    '''Function to get settings from ENV File'''
    return settings()