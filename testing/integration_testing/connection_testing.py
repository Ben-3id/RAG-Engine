import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))


import os
import pytest 
from src.settings.config import get_settings
from sqlalchemy.ext.asyncio import create_async_engine 

url =  "postgresql+asyncpg://{POSTGRES_USERNAME}:{POSTGRES_PASSWORD}@pgvector:{DB_PORT}/{DB_NAME}"


@pytest.fixture
def engine():

    connection = url.format(
        POSTGRES_USERNAME = os.environ["POSTGRES_USERNAME"] ,
        POSTGRES_PASSWORD = os.environ["POSTGRES_PASSWORD"] ,
        DB_PORT = os.environ["DB_PORT"] ,
        DB_NAME = os.environ["DB_NAME"] 
    )

    engine = create_async_engine(connection)
    yield engine

def test_connection(engine):
    assert engine is not None