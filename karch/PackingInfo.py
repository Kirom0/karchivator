import os


class PackingInfo:
    def __init__(self, file_path):
        self.path = file_path
        self.full_size = os.path.getsize(file_path) # В байтах
        self.compressed_size = self.full_size # В байтах

        self.file_pure_path = file_path