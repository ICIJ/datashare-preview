from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi_utils.tasks import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, FileResponse, JSONResponse
from fastapi.concurrency import run_in_threadpool
from importlib.metadata import version
from preview_generator.exception import UnsupportedMimeType
from subprocess import TimeoutExpired
from typing import Dict, Any, Union

from dspreview.cache import DocumentCache
from dspreview.config import settings
from dspreview.document import Document, DocumentTooBig, DocumentRootTooBig, DocumentNotPreviewable, DocumentUnauthorized, UnsafeDocumentIdentifier
from dspreview.preview import get_size_height
from dspreview.utils import is_truthy


def has_session_cookie(request: Request) -> bool:
    """
    Check if the request has a session cookie.

    Args:
        request (Request): The incoming request.

    Returns:
        bool: True if the session cookie is present, False otherwise.
    """
    enabled = is_truthy(settings.ds_session_cookie_enabled)
    name = settings.ds_session_cookie_name
    return enabled and name in request.cookies


def has_session_header(request: Request) -> bool:
    """
    Check if the request has a session header.

    Args:
        request (Request): The incoming request.

    Returns:
        bool: True if the session header is present, False otherwise.
    """
    enabled = is_truthy(settings.ds_session_header_enabled)
    name = settings.ds_session_header_name
    return enabled and name in request.headers


def get_cookies_from_forwarded_headers(request: Request) -> Dict[str, str]:
    """
    Get cookies from forwarded headers.

    Args:
        request (Request): The incoming request.

    Returns:
        Dict[str, str]: A dictionary of cookies extracted from headers.
    """
    if not has_session_cookie(request) and has_session_header(request):
        session_cookie_name = settings.ds_session_cookie_name
        session_header_name = settings.ds_session_header_name
        cookies = dict()
        cookies[session_cookie_name] = request.headers.get(
            session_header_name, '')
        return cookies
    return request.cookies


async def get_preview_generator_params(request: Request, document: Document, page: int) -> Dict[str, Any]:
    """
    Get parameters for the preview generator.

    Args:
        request (Request): The incoming request.
        document (Document): The document to generate a preview for.
        page (int): The page to generate a preview for.

    Returns:
        Dict[str, Any]: A dictionary of parameters for the preview generator.
    """
    size = request.query_params.get('size', 'xs')
    height = get_size_height(size)
    cookies = await authorize_document(request, document)
    await document.download_document(cookies)
    file_path = document.target_path_without_ext
    file_ext = document.target_ext
    return dict(file_path=file_path, file_ext=file_ext, height=height, page=page)


async def authorize_document(request: Request, document: Document) -> Dict[str, str]:
    """
    Download the document meta and check the user can preview it.

    Args:
        request (Request): The incoming request.
        document (Document): The requested document.

    Returns:
        Dict[str, str]: The cookies to download the document with.
    """
    cookies = get_cookies_from_forwarded_headers(request)
    await document.download_meta(cookies)
    await document.check_user_authorization(cookies)
    return cookies


def get_request_document(request: Request) -> Document:
    """
    Get the request document.

    Args:
        request (Request): The incoming request.

    Returns:
        Document: The document requested in the request.
    """
    index = request.path_params['index']
    id = request.path_params['id']
    routing = request.query_params.get('routing', None)
    return Document(index, id, routing)

@asynccontextmanager
async def lifespan(_app: FastAPI):
    await remove_expired_tokens_task()
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[settings.ds_session_header_name],
)


ERROR_RESPONSES = {
    DocumentTooBig: (413, "Document too big"),
    DocumentRootTooBig: (413, "Document root too big"),
    DocumentUnauthorized: (401, "Unauthorized"),
    UnsafeDocumentIdentifier: (400, "Invalid document identifier"),
}

NOT_PREVIEWABLE_ERRORS = (DocumentNotPreviewable, UnsupportedMimeType, TimeoutExpired)


async def respond_with_error_status(_request: Request, error: Exception) -> JSONResponse:
    status_code, detail = ERROR_RESPONSES[type(error)]
    return JSONResponse({"detail": detail}, status_code=status_code)


for error_class in ERROR_RESPONSES:
    app.add_exception_handler(error_class, respond_with_error_status)


@repeat_every(seconds=60 * 10)
async def remove_expired_tokens_task() -> None:
    max_age = int(settings.ds_document_max_age)
    DocumentCache(max_age).purge()


@app.get("/", response_class=PlainTextResponse, response_model=str)
async def home() -> str:
    """
    Home endpoint.

    Returns:
        str: A string indicating the version of Datashare preview.
    """
    try:
        return 'Datashare preview v%s' % version("datashare_preview")
    except ImportError:
        return 'Datashare preview'


@app.get("/api/v1/thumbnail/{index}/{id}.json", response_model=None)
async def info(request: Request, page: int = Query(0, ge=0)) -> Union[Dict[str, Any], HTTPException]:
    """
    Get information about a document.

    Args:
        request (Request): The incoming request.

    Returns:
        Union[Dict[str, Any], HTTPException]: A dictionary containing document information or an HTTP exception.
    """
    document = get_request_document(request)
    try:
        await get_preview_generator_params(request, document, page)
        pages = await run_in_threadpool(document.get_manager_page_nb)
        # Disabled content preview if not requested explicitly
        if request.query_params.get('include-content'):
            content = await run_in_threadpool(document.get_json_preview)
        else:
            content = None
        return {
            'content': content,
            'content_type': document.target_content_type,
            'pages': pages,
            'previewable': True,
        }
    except NOT_PREVIEWABLE_ERRORS:
        document.delete_target_dir()
        return {'pages': 0, 'previewable': False}


@app.get("/api/v1/thumbnail/{index}/{id}", response_model=None)
async def thumbnail(request: Request, page: int = Query(0, ge=0)) -> Union[FileResponse, HTTPException]:
    """
    Get a document thumbnail.

    Args:
        request (Request): The incoming request.

    Returns:
        Union[FileResponse, HTTPException]: A FileResponse containing the thumbnail or an HTTP exception.
    """
    document = get_request_document(request)
    try:
        params = await get_preview_generator_params(request, document, page)
        preview_path = await run_in_threadpool(document.get_jpeg_preview, params)
    except NOT_PREVIEWABLE_ERRORS:
        document.delete_target_dir()
        raise HTTPException(status_code=415, detail="Document not previewable")
    return FileResponse(preview_path)


@app.get("/api/v1/pdf/{index}/{id}", response_model=None)
async def pdf(request: Request) -> Union[FileResponse, HTTPException]:
    """
    Get a document converted to PDF.

    Args:
        request (Request): The incoming request.

    Returns:
        Union[FileResponse, HTTPException]: A FileResponse containing the PDF or an HTTP exception.
    """
    document = get_request_document(request)
    try:
        cookies = await authorize_document(request, document)
        if not document.is_content_type_pdf_convertible:
            raise HTTPException(status_code=415, detail="Document not convertible to PDF")
        await document.download_document(cookies)
        pdf_path = await run_in_threadpool(document.get_pdf_preview)
    except NOT_PREVIEWABLE_ERRORS:
        document.delete_target_dir()
        raise HTTPException(status_code=415, detail="Document not previewable")
    return FileResponse(pdf_path, media_type='application/pdf')
