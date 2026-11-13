from typing import Any


def is_falsy(value: Any = None) -> bool:
    """
    Check if a value is falsy.

    Args:
        value (Any, optional): The value to check. Default is None.

    Returns:
        bool: True if the value is falsy, False otherwise.
    """
    return value in [False, 'False', 'false', 0, 'no', '', None]


def is_truthy(value: Any = None) -> bool:
    """
    Check if a value is truthy.

    Args:
        value (Any, optional): The value to check. Default is None.

    Returns:
        bool: True if the value is truthy, False otherwise.
    """
    return not is_falsy(value)
