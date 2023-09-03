from enum import Enum

class MediaType(Enum):
    VIDEO = 1
    PHOTO = 2
    UNKNOWN = 3
    
    @staticmethod
    def get_file_type_from_link(link:str):
        if link.find(".mp4") != -1:
            return MediaType.VIDEO
        elif link.find(".jpg") != -1 or link.find(".png") != -1 or link.find(".jpeg") != -1:
            return MediaType.PHOTO
        else:
            return MediaType.UNKNOWN
