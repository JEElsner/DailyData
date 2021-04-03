from importlib import resources
import json

from sys import argv as __argv

from .config import load_config

config = load_config()
