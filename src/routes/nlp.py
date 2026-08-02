from controller import NLPController 
from model import ChunkModel , TopicModel ,PGVectorModel
from fastapi import  APIRouter , Request 
from fastapi.responses import JSONResponse , StreamingResponse
import json 
from .db_schema import  SearchRequeset
import logging
import time
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from camel_tools.disambig.mle import MLEDisambiguator
from arabicstopwords.arabicstopwords import is_stop
from camel_tools.utils.dediac import dediac_ar

mle = MLEDisambiguator.pretrained(model_name='calima-msa-r13')

nlp_router = APIRouter(prefix="/api/nlp")
logger = logging.getLogger("uvicorn")

@nlp_router.post("/index/{topic_name}")
async def index(topic_name:str , request:Request):

    chunk_model = ChunkModel(request.app.db_client)
    topic_model = TopicModel(request.app.db_client)
    topic = await topic_model.get_topic_or_create(topic=topic_name) 

    nlp_controller = NLPController(
        embeddings_model= request.app.embed_client , 
        generate_model= request.app.llm_client , 
        vector_model= PGVectorModel(request.app.db_client)
    )
    last_chunk_id = None

    while True:

        chunks = await chunk_model.get_topic_chunks(
            topic_id=topic.topic_id ,
            last_chunk_id= last_chunk_id
            )
        
        if not chunks:
            break
        await nlp_controller.index_into_vectordb(chunks=chunks , batch_size=1000)
        last_chunk_id = chunks[-1][2]

    return True



@nlp_router.get("/pgsearch/{topic_name}")
async def semactic_search(topic_name:str , user_req:SearchRequeset , request:Request):

    nlp_controller = NLPController(
        embeddings_model= request.app.embed_client , 
        generate_model= request.app.llm_client , 
        vector_model= PGVectorModel(request.app.db_client)
    )

    query = [user_req.query]
    limit = user_req.limit

    topic_model = TopicModel(request.app.db_client)

    start_topic = time.perf_counter()

    topic = await topic_model.get_topic_or_create(topic=topic_name)

    end_topic = time.perf_counter()
    logger.error(f"time get topic {(end_topic - start_topic) * 1000:.2f} ms")

    starrt_searchFunc = time.perf_counter()

    results = await nlp_controller.semantic_search(topic_id=topic.topic_id , query=query , limit= limit)

    end_searchFunc = time.perf_counter()
    logger.error(f"time get topic {(end_searchFunc - starrt_searchFunc) * 1000:.2f} ms")

    for result in results:
        yield {"score":result['score'] , 
                "text":result['text']}


@nlp_router.get("/tssearch/{topic_name}")
async def TSsearch(topic_name:str , user_req:SearchRequeset , request:Request):

    query = user_req.query
    limit = user_req.limit

    start_process = time.perf_counter()
    processed = mle.disambiguate(query.split())
    processed_query = " ".join([dediac_ar(d.analyses[0].analysis['lex']) for d in processed])
    filtered = " ".join([word for word in query.split() if not is_stop(processed_query)])

    logger.error(f"time for process query {(time.perf_counter() - start_process) *1000:.2f} ms")

    start_get_topic = time.perf_counter()
    chunk_model = ChunkModel(request.app.db_client)
    topic_model = TopicModel(request.app.db_client)
    topic = await topic_model.get_topic_or_create(topic=topic_name)
    logger.error(f"time for get topic obj {(time.perf_counter() - start_get_topic) *1000:.2f} ms")

    start_search = time.perf_counter()
    results = await chunk_model.text_search_by_topic(topic_id = topic.topic_id , query=filtered , limit=limit)
    logger.error(f"time for search {(time.perf_counter() - start_search) *1000:.2f} ms")

    for result in results:
        yield {"text":result['text']}


@nlp_router.get("/hybrid_search/{topic_name}")
async def hybrid_search(topic_name:str , user_req:SearchRequeset , request:Request):

    semantic_session = AsyncSession(request.app.engine ,  expire_on_commit=False)
    ts_session = AsyncSession(request.app.engine ,  expire_on_commit=False)

    chunk_model = ChunkModel(ts_session)

    nlp_controller = NLPController(
        embeddings_model= request.app.embed_client , 
        generate_model= request.app.llm_client , 
        vector_model= PGVectorModel(semantic_session)
    )

    query = user_req.query
    limit = user_req.limit

    topic_model = TopicModel(request.app.db_client)
    topic = await topic_model.get_topic_or_create(topic=topic_name)


    start_search = time.perf_counter()

    semantic_result , ts_result = await asyncio.gather(
        nlp_controller.semantic_search(
            topic_id=topic.topic_id ,
            query=[query] , limit= limit
            ) ,
        chunk_model.text_search_by_topic(
            topic_id = topic.topic_id ,
            query=query ,
            limit=limit
            )  )
    
    end_search = time.perf_counter()
    logger.error(f"search time {(end_search - start_search) * 1000:.2f} ms")


    start_rank = time.perf_counter()

    final_results = nlp_controller.rrf([semantic_result , ts_result] , K=60)

    end_rank = time.perf_counter()
    logger.error(f"search time {(start_rank - end_rank) * 1000:.2f} ms")
    
    for result in final_results:
        yield {"score":result['rrf_score'] , 
                "text":result['text']}



@nlp_router.post('/hnsw/{topic_name}')
async def hnsw(topic_name , request:Request):
    vector_model = PGVectorModel(request.app.db_client)
    return await vector_model.hnsw_index()
