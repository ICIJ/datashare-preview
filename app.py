import os
from flask import Flask, send_file, abort, request
from preview_generator.manager import PreviewManager
from pathlib import Path

app = Flask(__name__)

FILES_ROOT_PATH = os.environ.get('FILES_ROOT_PATH', './samples')
CACHE_PATH = os.environ.get('CACHE_PATH', './cache')

def in_root_path(child_path):
    root = Path(FILES_ROOT_PATH)
    child = Path(child_path)
    return root in child.parents

def get_jpeg_preview(file_to_preview_path, cache_path = CACHE_PATH):
    manager = PreviewManager(cache_path, create_folder = True)
    return manager.get_jpeg_preview(file_to_preview_path)

@app.route('/api/v1/preview/')
def preview():
    path = request.args.get('file', None)
    # The file is not authorized
    if path is None or not in_root_path(path): abort(401)
    # If it not working, PreviewManager will raise an exception
    try: return send_file(get_jpeg_preview(path), as_attachment=False)
    # Silently fail
    except Exception as e: abort(500, e)
