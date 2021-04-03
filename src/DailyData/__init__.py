from importlib import resources
import json

from sys import argv as __argv

from .config import load_config

master_config = load_config()
