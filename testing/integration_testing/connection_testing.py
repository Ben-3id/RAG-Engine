import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))



import pytest 
from src.settings.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine 

url =  "postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@pgvector:{DB_PORT}/{DB_NAME}"

@pytest.fixture
def config():
    return get_settings()

def test_config(config):
    assert config is not None

@pytest.fixture
def engine(config):
    POSTGRES_USERNAME = config.POSTGRES_USERNAME
    POSTGRES_PASSWORD = config.POSTGRES_PASSWORD
    DB_PORT = config.DB_PORT
    DB_NAME = config.DB_NAME

    connection = url.format(
        POSTGRES_USERNAME = POSTGRES_USERNAME ,
        POSTGRES_PASSWORD = POSTGRES_PASSWORD ,
        DB_PORT = DB_PORT ,
        DB_NAME = DB_NAME 
    )

    engine = create_async_engine(connection)
    yield engine

def test_connection(engine):
    assert engine is not None