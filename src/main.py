from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from stores.embeddings import EmbeddingFactory
from stores.llm import GeneratorFactory
from fastapi import FastAPI
from settings import get_settings
from contextlib import asynccontextmanager
from model import ChunkModel , TopicModel ,PGVectorModel
from controller import NLPController
from routes import data_router , nlp_router

async def StartSpain( app:FastAPI ):
    app.settings = get_settings()
    url_connection = f"postgresql+asyncpg://{app.settings.POSTGRES_USERNAME}:{app.settings.POSTGRES_PASSWORD}@localhost:5400/{app.settings.DB_NAME}"
    app.engine = create_async_engine(url= url_connection)
    app.db_client = AsyncSession(bind=app.engine , expire_on_commit=False)
    chunk_session = AsyncSession(bind=app.engine , expire_on_commit=False)
    pgvector_session = AsyncSession(bind=app.engine , expire_on_commit=False)
    
    emb_factory = EmbeddingFactory(app.settings)
    app.embed_client = emb_factory.create(app.settings.EMBED_PROVIDER)

    llm_factory = GeneratorFactory(app.settings)
    app.llm_client = llm_factory.create(app.settings.LLM_PROVIDER)

    app.topic_model = TopicModel(app.db_client)
    app.chunk_model = ChunkModel(chunk_session)
    app.pgvector_model = PGVectorModel(pgvector_session)

    app.nlp_ctrl = NLPController(
        embeddings_model=app.embed_client,
        generate_model=app.llm_client,
        vector_model=app.pgvector_model
    )
    
async def EndSpain( app: FastAPI ):
    await app.engine.dispose()


@asynccontextmanager
async def LifeSpan(app:FastAPI):
    await StartSpain(app)

    yield

    await EndSpain(app)


app = FastAPI(lifespan=LifeSpan)
app.include_router(data_router)
app.include_router(nlp_router)
