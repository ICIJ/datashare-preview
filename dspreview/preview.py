SIZES = dict(xs=80, sm=310, md=540, lg=720, xl=960)


def get_size_height(size: str) -> int:
    """
    Get the height associated with a size.

    Args:
        size (str): The size identifier, which can be one of 'xs', 'sm', 'md', 'lg', 'xl' or a numeric value.

    Returns:
        int: The height value associated with the size.
    """
    if str(size).isnumeric():
        return int(size)
    else:
        return SIZES.get(size, SIZES.get('xs'))
