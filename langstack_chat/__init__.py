from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("langstack_chat")
except PackageNotFoundError:
    __version__ = "0.1"

__all__ = ["__version__"]
