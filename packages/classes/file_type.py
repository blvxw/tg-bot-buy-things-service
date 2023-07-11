from enum import Enum

class FileType(Enum):
    VIDEO = 1
    PHOTO = 2
    UNKNOWN = 3
    
    #? don`t use method endswith() because it is link to file in firebase storage 
    #? and it is not end with .mp4 or .jpg 
    @staticmethod
    def get_file_type_from_link(link:str):
        if link.find(".mp4") != -1:
            return FileType.VIDEO
        elif link.find(".jpg") != -1 or link.find(".png") != -1 or link.find(".jpeg") != -1:
            return FileType.PHOTO
        else:
            return FileType.UNKNOWN