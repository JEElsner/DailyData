from .config import load_config

master_config = load_config()

from . import _version
__version__ = _version.get_versions()['version']
