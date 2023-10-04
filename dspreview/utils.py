from functools import wraps
from typing import Any, Union


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


def hash_dict(func):
    """
    Transform mutable dictionaries into immutable dictionaries.

    Useful to be compatible with caching mechanisms.

    Args:
        func (callable): The function to wrap.

    Returns:
        callable: A wrapped function that converts mutable dictionaries to immutable ones.
    """
    class HDict(dict):
        def __hash__(self):
            return hash(frozenset(self.items()))

    @wraps(func)
    def wrapped(*args, **kwargs):
        args = tuple([HDict(arg) if isinstance(
            arg, dict) else arg for arg in args])
        kwargs = {k: HDict(v) if isinstance(v, dict)
                  else v for k, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapped
