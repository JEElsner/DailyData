from sys import argv

from .. import config
from . import Journaller


Journaller(config.tracker).record_and_write_to_file()
