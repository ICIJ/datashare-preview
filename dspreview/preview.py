SIZES = dict(xs=80, sm=310, md=540, lg=720, xl=960)

def get_size_height(size):
    if str(size).isnumeric():
        return int(size)
    else:
        return SIZES.get(size, SIZES.get('xs'))
