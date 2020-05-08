"""
Azure Blob Storage Module Class
"""
import typing
import time
import urllib


class AzureBlobStorage:

    def download_tar_file(self, tar_file_uri: str, output_path: str = 'repository.tar') -> str:
        urllib.request.urlretrieve(tar_file_uri, output_path)
        return output_path
