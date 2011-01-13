# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

BUS_INTERFACE_NAME = "org.ude.components.host"
BUS_OBJECT_PATH = "/org/ude/components/host"
GLADE_PREFIX = "/home/dan/Desktop/Programming/ude/ude-components/Host/"
MAIN_TABBED = "/home/dan/Desktop/Programming/ude/ude-components/Host/main-tabbed.py"

import logging,os

logger = logging.getLogger('Host')
logger.setLevel(logging.DEBUG)

__fh = logging.FileHandler('runtime.log')
__fh.setLevel(logging.DEBUG)

__ch = logging.StreamHandler()
__ch.setLevel(logging.ERROR)

__formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
__fh.setFormatter(__formatter)
__ch.setFormatter(__formatter)

logger.addHandler(__fh)
logger.addHandler(__ch)

try:
	GLADE_PREFIX = os.environ["GLADE_PREFIX"]
except KeyError:
	logger.info("No Glade Environment")


