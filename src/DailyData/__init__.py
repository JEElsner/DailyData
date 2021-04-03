from importlib import resources
import json

from sys import argv as __argv

from .config import Configuration

if resources.is_resource(__name__, 'config.json'):
    # TODO change to importlib instead of pkg_resources
    config = Configuration(
        **json.loads(resources.read_text(__name__, 'config.json')))
else:
    # Create default configuration if one doesn't exist
    config = Configuration()
