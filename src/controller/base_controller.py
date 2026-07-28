from settings import get_settings
import os
from pathlib import Path

class BaseController:
    def __init__(self):
        self.settings = get_settings()
        self.base_folder_path = Path(__file__).parent.parent
        self.asset_folder_path = os.path.join(self.base_folder_path ,"assets")

    def get_topic_folder_path(self , topic_name:str):
        path = os.path.join(self.asset_folder_path , topic_name)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
