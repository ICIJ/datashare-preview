import os
from flask import Flask, send_file, abort, request
from preview_generator.manager import PreviewManager
from pathlib import Path

app = Flask(__name__)
sizes = dict(xs=80, sm=310, md=540, lg=720, xl=960)

FILES_ROOT_PATH = os.environ.get('FILES_ROOT_PATH', './samples')
CACHE_PATH = os.environ.get('CACHE_PATH', './cache')

def in_root_path(child_path):
    root = Path(FILES_ROOT_PATH)
    child = Path(child_path)
    return root in child.parents

def get_jpeg_preview(params, cache_path = CACHE_PATH):
    manager = PreviewManager(cache_path, create_folder = True)
    return manager.get_jpeg_preview(**params)

def get_size_width(size):
    if str(size).isnumeric():
        return int(size)
    else:
        return sizes.get(size, sizes.get('xs'))

def get_preview_generator_params():
    file_path = request.args.get('file_path', None)
    size = request.args.get('size', 'xs')
    page = request.args.get('page', 1)
    return dict(file_path=file_path, width=get_size_width(size), page=int(page))

@app.route('/api/v1/thumbnail/')
def preview():
    params = get_preview_generator_params()
    # The file is not authorized
    if params['file_path'] is None or not in_root_path(params['file_path']): abort(401)
    # If it not working, PreviewManager will raise an exception
    try: return send_file(get_jpeg_preview(params), as_attachment=False)
    # Silently fail
    except Exception as e: abort(500, e)
