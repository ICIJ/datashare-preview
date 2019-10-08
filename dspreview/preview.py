import os
from preview_generator.manager import PreviewManager
from dspreview.spreadsheet import is_content_type_spreadsheet, is_ext_spreadsheet, get_spreadsheet_preview
from tempfile import gettempdir

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())
SIZES = dict(xs=80, sm=310, md=540, lg=720, xl=960)

def build_preview_manager():
    return PreviewManager(CACHE_PATH, create_folder = True)

def get_jpeg_preview(params):
    manager = build_preview_manager()
    return manager.get_jpeg_preview(**params)

def get_json_preview(params, content_type):
    file_ext = params['file_ext']
    file_path = params['file_path']
    # Only spreadsheet preview is supported yet
    if is_content_type_spreadsheet(content_type) or is_ext_spreadsheet(file_ext):
        return get_spreadsheet_preview(params)
    else:
        return None

def is_content_type_previewable(content_type):
    manager = build_preview_manager()
    return content_type in manager.get_supported_mimetypes()

def get_size_width(size):
    if str(size).isnumeric():
        return int(size)
    else:
        return SIZES.get(size, SIZES.get('xs'))
