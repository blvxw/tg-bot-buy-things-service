from enum import Enum

class FileType(Enum):
    VIDEO = 1
    PHOTO = 2
    UNKNOWN = 3
    @staticmethod
    def get_file_type(file_name):
        if file_name.endswith(".mp4"):
            return FileType.VIDEO
        elif file_name.endswith(".jpg") or file_name.endswith(".png") or file_name.endswith(".jpeg"):
            return FileType.PHOTO
        else:
            return FileType.UNKNOWN