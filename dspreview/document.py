import os
import httpx
from pathlib import Path
from shutil import rmtree
from tempfile import mkstemp
from typing import Optional, Dict, Any

from dspreview.content_types import SUPPORTED_CONTENT_TYPES
from dspreview.cache import THUMBNAILS_PATH, DOCUMENTS_PATH
from dspreview.config import settings
from dspreview.spreadsheet import is_content_type_spreadsheet, get_spreadsheet_preview
from preview_generator.manager import PreviewManager
from urllib.parse import quote, urljoin

REQUEST_TIMEOUT_SECONDS = 30


class Document:
    """
    Represents a document, allowing various operations such as fetching metadata, 
    downloading content, and generating previews.
    """

    def __init__(self, index: str, id: str, routing: Optional[str] = None) -> None:
        """
        Initialize a Document instance.

        Args:
            index (str): The index associated with the document.
            id (str): Unique identifier for the document.
            routing (str, optional): The routing associated with the document. Defaults to None.
        """
        raise_if_unsafe_identifier(index)
        raise_if_unsafe_identifier(id)
        if routing is not None:
            raise_if_unsafe_identifier(routing)
        self.index = index
        self.id = id
        self.routing = routing
        self.source: Dict[str, Any] = {}
        self.setup_target_directory()
        self.manager = PreviewManager(self.thumbnail_directory, create_folder=True)
        self.root: Optional[Document] = Document(index=index, id=self.routing) if self.is_embedded else None


    @property
    def meta_url(self) -> str:
        """Constructs and returns the URL to fetch the document's metadata."""
        url = urljoin(settings.ds_host, settings.ds_document_meta_path %
                      (self.index, self.id))
        # Optional routing parameter
        if self.routing is not None:
            url = urljoin(
                url, '?_source=contentLength,contentType,path&routing=%s' % quote(self.routing, safe=''))
        return url


    @property
    def src_url(self) -> str:
        """Constructs and returns the URL to fetch the document's content."""
        url = urljoin(settings.ds_host, settings.ds_document_src_path %
                      (self.index, self.id))
        # Optional routing parameter
        if self.routing is not None:
            url = urljoin(url, '?routing=%s' % quote(self.routing, safe=''))
        return url


    @property
    def target_path(self) -> str:
        if self.target_ext == '':
            return os.path.join(self.target_directory, 'raw')
        else:
            return os.path.join(self.target_directory, 'raw' + self.target_ext)


    @property
    def target_directory(self) -> str:
        return os.path.join(DOCUMENTS_PATH, self.index, self.id)


    @property
    def target_ext(self) -> str:
        if self.target_path_ext == '':
            if self.target_content_type is None:
                return ''
            return self.manager.get_file_extension(self.target_content_type)
        return self.target_path_ext


    @property
    def target_path_ext(self) -> str:
        return Path(self.source.get('path', '')).suffix


    @property
    def target_path_without_ext(self) -> str:
        return str(Path(self.target_path).with_suffix(''))


    @property
    def target_content_type(self) -> Optional[str]:
        return self.source.get('contentType', None)


    @property
    def thumbnail_directory(self) -> str:
        return os.path.join(THUMBNAILS_PATH, self.index, self.id)


    @property
    def is_embedded(self) -> bool:
        return self.routing and self.routing != self.id


    @property
    def content_length(self) -> int:
        return self.source.get('contentLength', -1)


    @property
    def target_content_length(self) -> int:
        if not self.target_exists:
            return -1
        return Path(self.target_path).stat().st_size
    

    @property
    def is_content_type_not_previewable(self) -> bool:
        return self.target_content_type not in SUPPORTED_CONTENT_TYPES


    @property
    def is_too_big(self) -> bool:
        return self.content_length > int(settings.ds_document_max_size)
    

    @property
    def is_target_too_big(self) -> bool:
        return self.target_content_length > int(settings.ds_document_max_size)
    
    
    @property
    def target_exists(self) -> bool:
        return Path(self.target_path).exists()


    def setup_target_directory(self) -> None:
        """
        Sets up the target directory for storing the document.
        """
        return os.makedirs(self.target_directory, exist_ok=True)


    async def download_document_with_stream(self, cookies: Dict[str, str]) -> str:
        """
        Asynchronously downloads the document using a streaming approach.

        Args:
            cookies (dict): Cookies for the HTTP request.

        Returns:
            str: Path to the downloaded document.
        """
        # Download meta if none
        if not self.source:
            await self.download_meta(cookies)
        async with httpx.AsyncClient(cookies=cookies, timeout=REQUEST_TIMEOUT_SECONDS) as client:
            async with client.stream('GET', self.src_url) as response:
                if 400 <= response.status_code < 500:
                    raise DocumentUnauthorized()
                if response.status_code != httpx.codes.OK:
                    raise DocumentNotPreviewable()
                await self.write_response_to_target(response)
        return self.target_path


    async def write_response_to_target(self, response: httpx.Response) -> None:
        """
        Write the response body to the target path, chunk by chunk.

        The body goes to a temporary file first so a concurrent request never
        previews a partially written document, and two concurrent downloads
        never write into the same file. The download stops as soon as it
        exceeds the max size, because Datashare may not report a content length.
        """
        max_size = int(settings.ds_document_max_size)
        partial_descriptor, partial_path = mkstemp(dir=self.target_directory, suffix='.partial')
        written_size = 0
        try:
            with os.fdopen(partial_descriptor, 'wb') as file:
                async for chunk in response.aiter_bytes():
                    written_size += len(chunk)
                    if written_size > max_size:
                        raise DocumentTooBig()
                    file.write(chunk)
            os.replace(partial_path, self.target_path)
        finally:
            Path(partial_path).unlink(missing_ok=True)


    async def download_document(self, cookies: Dict[str, str]) -> str:
        """
        Asynchronously downloads the document if it doesn't exist locally.

        Args:
            cookies (dict): Cookies for the HTTP request.

        Returns:
            str: Path to the downloaded document.
        """
        # Ensure the file doesn't exist locally
        if not self.target_exists:
            # Download the document using streaming
            await self.download_document_with_stream(cookies)
        # Ensure the downloaded file doesn't eceed
        if self.is_target_too_big:
            # Delete the target to ensure we don't keep
            # on disk document that are too big 
            self.delete_target_dir()
            # Raise an error, we can't do anything
            raise DocumentTooBig()
        return self.target_path


    async def download_meta(self, cookies: Dict[str, str]) -> None:
        """
        Asynchronously downloads the document's metadata.

        Args:
            cookies (dict): Cookies for the HTTP request.

        Raises:
            DocumentUnauthorized: If the document request is unauthorized.
            DocumentNotPreviewable: If the document is not previewable.
        """
        async with httpx.AsyncClient(cookies=cookies, timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(self.meta_url)
            # Raise exception if the document request didn't succeed
            if response.status_code >= 400 and response.status_code < 500:
                raise DocumentUnauthorized()
            # Any other error
            elif response.status_code != httpx.codes.OK:
                raise DocumentNotPreviewable()
            data = response.json()
            # Save the source meta
            self.source = data.get('_source', {})
            # Download root meta as well if embedded
            if self.is_embedded:
                await self.root.download_meta(cookies)


    async def check_user_authorization(self, cookies: Dict[str, str]) -> None:
        """
        Checks user authorization to access the document.

        Args:
            cookies (dict): Cookies for the HTTP request.

        Raises:
            DocumentNotPreviewable: If the document is not previewable.
            DocumentTooBig: If the document is too big to preview.
            DocumentRootTooBig: If the embedded document's root is too big to preview.
        """
        if not self.source:
            await self.download_meta(cookies)
        if self.is_content_type_not_previewable:
            raise DocumentNotPreviewable()
        if self.is_too_big:
            raise DocumentTooBig()
        if self.is_embedded and self.root.is_too_big:
            raise DocumentRootTooBig()


    def delete_target_dir(self) -> None:
        """
        Remove the target directory if it exists.
        """
        return rmtree(self.target_directory, ignore_errors=True)


    def get_jpeg_preview(self, params: Dict[str, Any]) -> str:
        """
        Generate a JPEG preview of the document.

        Args:
            params (dict): Additional parameters for generating the preview.

        Returns:
            str: Path to the generated JPEG preview.
        """
        params = {**params, **dict(file_path=self.target_path)}
        return self.manager.get_jpeg_preview(**params)


    def get_json_preview(self) -> Any:
        """
        Generate a JSON preview of the document if supported (currently for spreadsheets).

        Returns:
            Any: The JSON preview data, or None if unsupported.
        """
        if is_content_type_spreadsheet(self.target_content_type):
            return get_spreadsheet_preview(self.target_path)
        else:
            return None
        
        
    def get_manager_page_nb(self) -> int:
        """
        Get the number of pages in the document managed by the PreviewManager.

        Returns:
            int: The number of pages in the document.
        """
        return self.manager.get_page_nb(self.target_path)
    


def raise_if_unsafe_identifier(identifier: str) -> None:
    """
    Index, id and routing become directory names in the cache, so they must not
    point outside of it.
    """
    is_relative_directory = identifier in ('.', '..')
    has_path_separator = '/' in identifier or os.sep in identifier
    if is_relative_directory or has_path_separator:
        raise UnsafeDocumentIdentifier(identifier)


class UnsafeDocumentIdentifier(Exception):
    """Exception raised when an index, id or routing could escape the cache directory."""

    def __init__(self, identifier: str) -> None:
        super().__init__(f'Unsafe document identifier: {identifier!r}')
        self.identifier = identifier


class DocumentUnauthorized(Exception):
    """Exception raised when there's an unauthorized access attempt to a document."""

class DocumentNotPreviewable(Exception):
    """Exception raised when a document is not previewable."""

class DocumentRootTooBig(Exception):
    """Exception raised when the root document's size exceeds the allowable limit."""

class DocumentTooBig(Exception):
    """Exception raised when the document's size exceeds the allowable limit."""
