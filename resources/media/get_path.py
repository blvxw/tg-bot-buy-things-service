import os

def getPathToMediaFolder():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"


def getPathToMediaFolderWithoutSlash():
    return os.path.dirname(os.path.abspath(__file__)) + "\\"