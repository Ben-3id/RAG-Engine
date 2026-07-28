from .base_controller import BaseController
import shutil
from fastapi import UploadFile
import os
from model.enum import ResponseEnum
import string , random
import hashlib
from model import AssetModel
from  langdetect import detect , DetectorFactory
from pypdf import PdfReader

class DataController(BaseController):
    mb2byte = 1048576
    def __init__(self):
        super().__init__()

    def validate_file(self, file:UploadFile):
        signals = {"Test_size" :ResponseEnum.FILE_SIZE_ACCEPTED.value,"Test_Type":ResponseEnum.SUPPORTED_TYPE.value}
        valid = True

        if file.size > (self.settings.FILE_SIZE * DataController.mb2byte):
            signals["Test_size"]=ResponseEnum.FILE_SIZE_EXCCED.value
            valid = False

        if not file.content_type in  self.settings.FILE_TYPES:
            signals["Test_Type"] = ResponseEnum.NOT_SUPPORTED_TYPE.value
            valid = False

        return valid , signals

    
    def save_file(self, file_path:str , file :UploadFile ):

        with open(file_path , 'wb') as buffer :
            shutil.copyfileobj(file.file , buffer)

        return file_path

    def generate_filename(self, file_name:str , len_str:int):

        return "".join(
            random.choices(string.ascii_letters + string.digits , k= len_str)
            ) +"_"+file_name
        
    def generate_unique_filepath(self, file_name:str , topic_name:str):

        len_str = self.settings.LEN_UNIQUE_STR
        topic_path = os.path.join(self.asset_folder_path , topic_name)
        unique_name = self.generate_filename(file_name=file_name , len_str=len_str)
        full_path = os.path.join(topic_path , unique_name)
        
        if not os.path.exists(topic_path):
            os.mkdir(topic_path)

        while os.path.exists(full_path):
            len_str += 1
            unique_name = self.generate_filename(file_name=file_name , len_str=len_str)
            full_path = os.path.join(topic_path , unique_name)

        return full_path , unique_name


    def get_hashfile(self , file :UploadFile):

        hash_func = hashlib.new(self.settings.HASH_ALGORITHM)
        file.seek(0)
        while chunk := file.read(8192):
            hash_func.update(chunk)
        file.seek(0)
        return hash_func.hexdigest()

    def language_detect(self, path:str):
        DetectorFactory.seed = 0
        sample = PdfReader(path).pages[0].extract_text() 
        language = detect(sample)
        return language

    def get_extention(self , path:str):
        return os.path.splitext(p= path)[-1]

