from enum import Enum


class ResponseEnum(Enum):
    FILE_SIZE_EXCCED = "File_Size_Excced"
    FILE_SIZE_ACCEPTED = "file_size_allowed"

    NOT_SUPPORTED_TYPE = "not_supported_type"
    SUPPORTED_TYPE = "supported_type"
    
    FILE_IS_EXISTS = "file_is_already_exists"
    FILE_ACCEPTED = "file_accepted"