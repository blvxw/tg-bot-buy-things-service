import pyrebase
from resources.config import firebaseConfig
from packages.classes.file_type import FileType
from resources.media.get_path import getPathToMediaFolder, getPathToMediaFolderWithoutSlash
from packages.patterns.singleton import Singleton
import requests


class FirebaseStorage(metaclass=Singleton):
    def __init__(self):
        self.storage = pyrebase.initialize_app(firebaseConfig).storage()

    def upload_file(self, file_name, product_id):
        path_to_file = getPathToMediaFolder() + file_name
        self.storage.child(f"media/{product_id}/{file_name}").put(path_to_file)

    def download_file(self, file_name, product_id):
        link = self.storage.child(f"media/{product_id}/{file_name}").get_url(None)
        response = requests.get(link)
        with open(getPathToMediaFolder() + file_name, 'wb') as file:
            file.write(response.content)

    def delete_file(self, file_name, product_id):
        self.storage.child(f"media/{product_id}/{file_name}").delete()

    def get_all_product_files(self, product_id):
        return self.storage.child(f"media/{product_id}").list_files()
