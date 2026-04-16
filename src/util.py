from typing import TypeVar

T = TypeVar("T")


def ann[T](value: T | None) -> T:
    """Assert that the value is not None."""
    assert value is not None
    return value
