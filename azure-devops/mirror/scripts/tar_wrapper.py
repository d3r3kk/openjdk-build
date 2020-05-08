"""
Tar Module Class
"""
import typing
import shutil

class Tar:

    def extract(self, input_file_path: str) -> str:
        extract_dir = "./repo"
        shutil.unpack_archive(input_file_path, extract_dir)
        return extract_dir

    def copy(self, input_file_path: str, output_file_path: str) ->None:
        shutil.copyfile(input_file_path, output_file_path)
