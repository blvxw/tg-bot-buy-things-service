import pyrebase
from resources.config import firebaseConfig
from resources.media.get_path import get_path_to_media_folder
from packages.patterns.singleton import Singleton


class FirebaseStorage(metaclass=Singleton):
    def __init__(self):
        self.storage = pyrebase.initialize_app(firebaseConfig).storage()

    def upload_file(self, file_name, folder_name):
        path_to_file = get_path_to_media_folder() + file_name
        self.storage.child(f"media/{folder_name}/{file_name}").put(path_to_file)

    def get_link_to_file(self, file_name, folder_name):
        return self.storage.child(f"media/{folder_name}/{file_name}").get_url(None)

    def delete_file(self, file_name, folder_name):
        self.storage.child(f"media/{folder_name}/{file_name}").delete()
