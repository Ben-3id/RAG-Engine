from .base_controller import BaseController
from .data_controller import DataController
from model.enum import ProcessEnum
from langchain_community.document_loaders import TextLoader , PyMuPDFLoader 
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger("uvicorn")

class ProcessController(BaseController):
    def __init__(self):
        super().__init__()


    def get_loader(self , path:str):
        ext = DataController().get_extention(path= path)
        lang = DataController().language_detect(path= path)
        logger.error(f"lang -----> {lang} ")
        if ext == ProcessEnum.TXT.value and lang == ProcessEnum.AR.value:
            return TextLoader(file_path= path , encoding= 'utf-8')

        elif ext == ProcessEnum.TXT.value and lang == ProcessEnum.EN.value:
            return TextLoader(file_path= path , encoding= 'utf-8')

        elif ext == ProcessEnum.PDF.value and lang == ProcessEnum.AR.value:
            pass

        elif ext == ProcessEnum.PDF.value and lang == ProcessEnum.EN.value:
            return PyMuPDFLoader(file_path=path)

        # elif ext == ProcessEnum.DOC and lang == ProcessEnum.AR:
        #     pass

        # elif ext == ProcessEnum.DOC and lang == ProcessEnum.EN:
        #     pass

        # elif ext == ProcessEnum.DOCX and lang == ProcessEnum.AR:
        #     pass

        # elif ext == ProcessEnum.DOCX and lang == ProcessEnum.EN:
        #     pass

        return None

    def sanitize_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        return text.replace("\x00", "")

    def get_file_content(self , path:str):
        loader = self.get_loader(path = path)
        if loader:
            return loader.load()
        return None

    def process_file_content(self , path:str , chunk_size:int = 1000 , chunk_overlap:int = 100):
        
        text_splitter = RecursiveCharacterTextSplitter(chunk_size = chunk_size , chunk_overlap = chunk_overlap)
        file_content = self.get_file_content(path=path)

        content_text = [self.sanitize_text(page.page_content) for page in file_content]
        metadata = [page.metadata for page in file_content]

        chunks = text_splitter.create_documents(
            content_text, metadatas=metadata
        )

        return chunks
