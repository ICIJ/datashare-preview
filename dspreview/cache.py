import logging
import os

from datetime import datetime
from glob import glob
from shutil import rmtree
from tempfile import gettempdir

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())
DOCUMENTS_PATH = os.path.join(CACHE_PATH, 'documents')
THUMBNAILS_PATH = os.path.join(CACHE_PATH, 'thumbnails')

class DocumentCache:

    def __init__(self, max_age: int = 1):
        self.max_age = max_age
        self.log = logging.getLogger(__name__)


    def is_directory_expired(self, dir: str):
        return datetime.now().timestamp() - os.path.getmtime(dir) > self.max_age


    def get_expired_documents(self):
        documents = glob(os.path.join(DOCUMENTS_PATH, '*/*/'))
        thumbnails = glob(os.path.join(THUMBNAILS_PATH, '*/*/'))
        directories = documents + thumbnails
        return [ dir for dir in directories if self.is_directory_expired(dir) ]


    def purge(self):
        for dir in self.get_expired_documents():
            self.log.info('Deleting cached directory %s' % dir)
            rmtree(dir)
