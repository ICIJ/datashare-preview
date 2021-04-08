import os
from tempfile import gettempdir

CACHE_PATH = os.environ.get('CACHE_PATH', gettempdir())
THUMBNAILS_PATH = os.path.join(CACHE_PATH, 'thumbnails')
SIZES = dict(xs=80, sm=310, md=540, lg=720, xl=960)

def get_size_width(size):
    if str(size).isnumeric():
        return int(size)
    else:
        return SIZES.get(size, SIZES.get('xs'))
