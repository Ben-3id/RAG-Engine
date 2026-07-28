from sqlalchemy.ext.asyncio import create_async_engine , AsyncSession
from stores.embeddings import EmbeddingFactory
from stores.llm import GeneratorFactory
from fastapi import FastAPI
from settings import get_settings
from contextlib import asynccontextmanager
from routes import data_router , nlp_router

async def StartSpain( app:FastAPI ):
    app.settings = get_settings()
    url_connection = f"postgresql+asyncpg://{app.settings.POSTGRES_USERNAME}:{app.settings.POSTGRES_PASSWORD}@localhost:5400/{app.settings.DB_NAME}"
    app.engine = create_async_engine(url= url_connection)
    app.db_client = AsyncSession(bind=app.engine , expire_on_commit=False)

    emb_factory = EmbeddingFactory(app.settings)
    app.embed_client = emb_factory.create(app.settings.EMBED_PROVIDER)

    llm_factory = GeneratorFactory(app.settings)
    app.llm_client = llm_factory.create(app.settings.LLM_PROVIDER)


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
