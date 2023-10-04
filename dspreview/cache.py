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
        """
        Initialize the DocumentCache with a maximum age for cached items.

        Args:
            max_age (int, optional): The maximum age (in seconds) for cached items. Default is 1 second.
        """
        self.max_age = max_age

    def is_directory_expired(self, directory: str) -> bool:
        """
        Check if a directory is expired based on its last modification time.

        Args:
            directory (str): The path to the directory to check.

        Returns:
            bool: True if the directory is expired, False otherwise.
        """
        return datetime.now().timestamp() - os.path.getmtime(directory) > self.max_age

    def get_expired_documents(self) -> List[str]:
        """
        Get a list of expired document directories.

        Returns:
            List[str]: A list of expired document directory paths.
        """
        documents = glob(os.path.join(DOCUMENTS_PATH, '*/*/'))
        thumbnails = glob(os.path.join(THUMBNAILS_PATH, '*/*/'))
        directories = documents + thumbnails
        return [dir for dir in directories if self.is_directory_expired(dir)]

    def purge(self) -> None:
        """
        Purge expired cached directories.

        This method deletes expired cached directories from the cache.
        """
        for directory in self.get_expired_documents():
            logger.info('Deleting cached directory %s' % directory)
            rmtree(directory)
