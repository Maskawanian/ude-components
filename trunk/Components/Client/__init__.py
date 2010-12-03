from Base import Base
SAVE_STATUS_SAVED               = 0 # We can close this without losing data.
SAVE_STATUS_NOT_SAVED           = 1 # If we close this we will lose data, but we can save.
SAVE_STATUS_NOT_SAVED_NEED_PATH = 2 # If we close this we will lose data, but we can save, however need the save path.
SAVE_STATUS_SAVING              = 3 # In the progress of saving.
SAVE_STATUS_UNSAVABLE           = 4 # If we close this we will lose data, we are not able to save however.
