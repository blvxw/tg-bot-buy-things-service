import pyrebase
from resources.config import firebaseConfig
from packages.classes.file_type import FileType
from resources.media.get_path import getPathToMediaFolder
from packages.patterns.singleton import Singleton
import requests


class FirebaseStorage(metaclass=Singleton):
    def __init__(self):
        self.storage = pyrebase.initialize_app(firebaseConfig).storage()

    def upload_file(self, file_name, folder_name):
        path_to_file = getPathToMediaFolder() + file_name
        self.storage.child(f"media/{folder_name}/{file_name}").put(path_to_file)

    def download_file(self, file_name, folder_name):
        link = self.storage.child(f"media/{folder_name}/{file_name}").get_url(None)
        response = requests.get(link)
        with open(getPathToMediaFolder() + file_name, 'wb') as file:
            file.write(response.content)

    def get_link_to_file(self, file_name, folder_name):
        return self.storage.child(f"media/{folder_name}/{file_name}").get_url(None)
    def get_all_product_files(self, folder_name):
        return self.storage.child(f"media/{folder_name}").list_files()

    def delete_file(self, file_name, folder_name):
        self.storage.child(f"media/{folder_name}/{file_name}").delete()

