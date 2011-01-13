# See LICENCE for the source code licence.
# (c) 2010 Dan Saul

from Base import Base

SAVE_STATUS_SAVED               = 0 # We can close this without losing data.
SAVE_STATUS_NOT_SAVED           = 1 # If we close this we will lose data, but we can save.
SAVE_STATUS_NOT_SAVED_NEED_PATH = 2 # If we close this we will lose data, but we can save, however need the save path.
SAVE_STATUS_SAVING              = 3 # In the progress of saving.
SAVE_STATUS_UNSAVABLE           = 4 # If we close this we will lose data, we are not able to save however.
SAVE_STATUS_RANGE               = range(SAVE_STATUS_SAVED,SAVE_STATUS_UNSAVABLE+1)

BUS_INTERFACE_NAME = "org.ude.components.client"
BUS_INTERFACE_NAME_PID_FORMAT = BUS_INTERFACE_NAME+"_{0}"
BUS_OBJECT_PATH = "/org/ude/components/client"

import logging,os

logger = logging.getLogger('Client')
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




