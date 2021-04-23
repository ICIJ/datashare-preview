import os

from datetime import datetime
from glob import glob
from fastapi.logger import logger
from shutil import rmtree
from tempfile import gettempdir
from typing import List

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())
DOCUMENTS_PATH = os.path.join(CACHE_PATH, 'documents')
THUMBNAILS_PATH = os.path.join(CACHE_PATH, 'thumbnails')

class DocumentCache:

    def __init__(self, max_age: int = 1) -> None:
        self.max_age = max_age


    def is_directory_expired(self, dir: str) -> bool:
        return datetime.now().timestamp() - os.path.getmtime(dir) > self.max_age


    def get_expired_documents(self) -> List[str]:
        documents = glob(os.path.join(DOCUMENTS_PATH, '*/*/'))
        thumbnails = glob(os.path.join(THUMBNAILS_PATH, '*/*/'))
        directories = documents + thumbnails
        return [ dir for dir in directories if self.is_directory_expired(dir) ]


    def purge(self) -> None:
        for dir in self.get_expired_documents():
            logger.info('Deleting cached directory %s' % dir)
            rmtree(dir)
