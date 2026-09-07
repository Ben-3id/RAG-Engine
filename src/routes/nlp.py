from controller import NLPController 
from model import ChunkModel , TopicModel ,PGVectorModel
from fastapi import  APIRouter , Request 
from fastapi.responses import JSONResponse , StreamingResponse
import json 
from .db_schema import  SearchRequeset
from ragas.embeddings import HuggingFaceEmbeddings
from stores.embeddings.providers.baai import BAAI
from ragas.llms import LiteLLMStructuredLLM , llm_factory
import litellm
from ragas import  aevaluate , EvaluationDataset
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness ,ContextPrecision
# from ragas.metrics.collections import ContextPrecision
import logging
import time
import dotenv
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from camel_tools.disambig.mle import MLEDisambiguator
from arabicstopwords.arabicstopwords import is_stop
from camel_tools.utils.dediac import dediac_ar
from stores.llm.providers.prompts.v1 import Get_prompt 
from stores.llm.providers.prompts.v2 import Get_promptv2



mle = MLEDisambiguator.pretrained(model_name='calima-msa-r13')

nlp_router = APIRouter(prefix="/api/nlp")
logger = logging.getLogger("uvicorn")

@nlp_router.post("/index/{topic_name}")
async def index(topic_name:str , request:Request):

    chunk_model = request.app.chunk_model
    topic_model = request.app.topic_model
    topic = await topic_model.get_topic_or_create(topic=topic_name) 

    nlp_controller = request.app.nlp_ctrl
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

    nlp_controller = request.app.nlp_ctrl

    query = [user_req.query]
    limit = user_req.limit

    topic_model = request.app.topic_model

    start_topic = time.perf_counter()

    topic_id = await topic_model.get_topic_or_create(topic=topic_name)

    end_topic = time.perf_counter()
    logger.error(f"time get topic {(end_topic - start_topic) * 1000:.2f} ms")

    starrt_searchFunc = time.perf_counter()

    results = await nlp_controller.semantic_search(topic_id=topic_id , query=query , limit= limit)

    end_searchFunc = time.perf_counter()
    logger.error(f"time total time search {(end_searchFunc - starrt_searchFunc) * 1000:.2f} ms")

    for result in results:
        yield {"score":result['score'] , 
                "text":result['text']}


@nlp_router.get("/tssearch/{topic_name}")
async def TSsearch(topic_name:str , user_req:SearchRequeset , request:Request):

    start_req_info = time.perf_counter()
    query = user_req.query
    limit = user_req.limit
    logger.error(f"time for get req info {(time.perf_counter() - start_req_info) *1000:.2f} ms")

    start_get_controller = time.perf_counter()
    nlp_controller = request.app.nlp_ctrl
    logger.error(f"time for get NLP Controller {(time.perf_counter() - start_get_controller) *1000:.2f} ms")

    start_get_topic = time.perf_counter()
    chunk_model = request.app.chunk_model
    topic_model = request.app.topic_model
    topic_id = await topic_model.get_topic_or_create(topic=topic_name)
    logger.error(f"time for get topic obj {(time.perf_counter() - start_get_topic) *1000:.2f} ms")

    start_search = time.perf_counter()
    results = await nlp_controller.lexical_search(topic_id = topic_id , chunk_model = chunk_model , query = query , limit=limit)
    logger.error(f"time for search {(time.perf_counter() - start_search) *1000:.2f} ms")

    return results


@nlp_router.get("/hybrid_search/{topic_name}")
async def hybrid_search(topic_name:str , user_req:SearchRequeset , request:Request):
    start_init = time.perf_counter()

    chunk_model = request.app.chunk_model

    nlp_controller = request.app.nlp_ctrl

    query = user_req.query
    limit = user_req.limit

    topic_model = request.app.topic_model
    topic_id = await topic_model.get_topic_or_create(topic=topic_name)

    end_init = time.perf_counter()
    logger.error(f" init setup time {(end_init - start_init) * 1000:.2f} ms")

    start_search = time.perf_counter()

    semantic_result , ts_result = await asyncio.gather(
        nlp_controller.semantic_search(
            topic_id=topic_id ,
            query=[query] , limit= limit
            ) ,
        nlp_controller.lexical_search(
            topic_id = topic_id ,
            chunk_model = chunk_model ,
            query=query ,
            limit=limit
            )  )
    
    end_search = time.perf_counter()
    logger.error(f"hybrid search time {(end_search - start_search) * 1000:.2f} ms")


    start_rank = time.perf_counter()

    final_results = nlp_controller.rrf([semantic_result , ts_result] , K=60)

    end_rank = time.perf_counter()
    logger.error(f"rank time {(end_rank - start_rank) * 1000:.2f} ms")
    
    return final_results


@nlp_router.post('/hnsw/{topic_name}')
async def hnsw(topic_name , request:Request):
    vector_model = PGVectorModel(request.app.db_client)
    return await vector_model.hnsw_index()




@nlp_router.post('/chat/{topic_name}')
async def chat(topic_name ,  user_req:SearchRequeset , request:Request):

    Model = request.app.llm_client
    chunks = await hybrid_search(topic_name= topic_name , user_req = user_req , request= request)
    prompt = Get_prompt(chunks= chunks , question=user_req.query)
    result = Model.generate_text(prompt)
    return "".join(result)
