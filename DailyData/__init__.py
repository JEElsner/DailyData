from .config import load_config

from . import _version
__version__ = _version.get_versions()['version']

master_config = load_config()
