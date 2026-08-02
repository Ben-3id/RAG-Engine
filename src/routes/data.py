from fastapi import APIRouter , Request , UploadFile , File , status
from fastapi.responses import JSONResponse
from controller import DataController , ProcessController
from model import AssetModel , TopicModel , ChunkModel
from routes.db_schema import ProcessRequest
from model.enum import ResponseEnum
from model.database.db_schema import Asset , Topic  , Chunk
from camel_tools.disambig.mle import MLEDisambiguator
from camel_tools.utils.dediac import dediac_ar
import logging
import os

data_router = APIRouter(prefix="/api/data")
logger = logging.getLogger("uvicorn")

@data_router.post("/upload/{topic_name}")
async def upload(topic_name:str , req:Request , file: UploadFile = File(...)):
    
    data_controller = DataController()
    topic_model = TopicModel(req.app.db_client)
    asset_model = AssetModel(req.app.db_client)

    valid , signals = data_controller.validate_file(file=file)

    if not valid: 
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content=signals)

    file_path , file_unique_name = data_controller.generate_unique_filepath(file_name=file.filename , topic_name=topic_name)

    filehash =  data_controller.get_hashfile(file.file)
    exist = await asset_model.is_asset_accept(filehash)

    if exist: 
        return JSONResponse(status_code= status.HTTP_400_BAD_REQUEST, content=ResponseEnum.FILE_IS_EXISTS.value)
    

    data_controller.save_file(file=file ,file_path=file_path)

    topic = Topic(topic_name= topic_name )
    topic = await topic_model.get_topic_or_create(topic)

    asset = Asset(topic_id = topic.topic_id ,
                  name= file_unique_name , 
                  size= file.size ,
                  type = file.content_type ,
                  filehash= filehash)
    
    _ = await asset_model.add_asset(asset= asset)

    return JSONResponse(
        content={   "file_unique_name" : file_unique_name,
                    "asset_id" : str(asset.asset_id) ,
                    "topic_id" : str(asset.topic_id)} ,
        status_code=status.HTTP_202_ACCEPTED
    )


@data_router.post('/process/{topic_name}')
async def process(topic_name:str , process_req:ProcessRequest, req:Request):
    file_name = process_req.file_name
    asset_id = process_req.asset_id
    chunk_size = process_req.chunk_size if process_req.chunk_size else 100
    overlap_size = process_req.overlap_size
    do_reset = process_req.do_reset
    batch_size = process_req.batch_size

    process_controller = ProcessController()
    mle = MLEDisambiguator.pretrained(model_name='calima-msa-r13')
    asset_model = AssetModel(req.app.db_client)
    topic_model = TopicModel(req.app.db_client)
    chunk_model = ChunkModel(req.app.db_client)


    topic = await topic_model.get_topic_or_create(topic=topic_name)

    asset_list = []
    if asset_id and topic.topic_id:
        asset_record = asset_model.get_asset(topic_id=topic.topic_id , asset_id=asset_id)
        asset_list.append(asset_record)
    else:
        asset_records = await asset_model.get_all_topic_assets(topic_id= topic.topic_id)
        asset_list = asset_records

    for asset in asset_list:
        path = process_controller.get_topic_folder_path(topic_name=topic_name)
        full_path = os.path.join(path , asset.name)
        logger.error(f"{full_path}")
        file_chunks = process_controller.process_file_content(path= full_path ,chunk_size=chunk_size ,chunk_overlap= overlap_size)
        chunks = []
        for chunk in file_chunks:
            sentence = chunk.page_content
            words = sentence.split()
            result = mle.disambiguate(words)
            processed = ' '.join([dediac_ar(d.analyses[0].analysis['lex']) for d in result])
            logger.error(f"camel --> {processed}")

            chunks.append(

            Chunk(
                asset_id = asset.asset_id,
                topic_id = topic.topic_id,
                text = chunk.page_content,
                chunk_metadata = chunk.metadata,
                processed_text = processed
                                )

            )
        _ = await chunk_model.insert_many_chunks(chunks=chunks , batch_size= batch_size)
    return len(chunks)