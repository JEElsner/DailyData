from sys import argv

from .. import master_config
from . import Journaller


Journaller(master_config.tracker).record_and_write_to_file()
