# -----------------------------------------------------------------------------
#
# SPDX-License-Identifier: MIT
#
# This file is part of the autorios project
#
# Detailed license information can be found in LICENSE
# at the top level directory.
#
# -----------------------------------------------------------------------------


#STL imports
from pathlib import Path
import logging
import shutil

#3rd party imports
import platformdirs

logger = logging.getLogger(__name__)

SYSTEM_SETTINGS_DIR_PATH = Path(platformdirs.site_config_dir()) / "autotrios"
USER_SETTINGS_DIR_PATH = Path(platformdirs.user_config_dir()) / "autotrios"
USER_LOGFILE = Path(platformdirs.user_log_dir()) / "autotrios.log"
USER_DATA_DIR = Path(platformdirs.user_data_dir()/"autotrios")

SYSTEM_SETTINGS_FILE_PATH = SYSTEM_SETTINGS_DIR_PATH / "settings.yaml"
USER_SETTINGS_FILE_PATH   = USER_SETTINGS_DIR_PATH / "settings.yaml"

PROTOCOL_CONFIG_DIR_PATH = USER_SETTINGS_DIR_PATH / "protocol_config"
SPECIMEN_NAMES_TEMPLATE_DIR_PATH=USER_SETTINGS_DIR_PATH/ "specimen_names"
SPECIMEN_NAMER_STATE_DIR_PATH = USER_DATA_DIR/ "specimen_namer"
SPECIMEN_NAMER_STATE_FILE_PATH = SPECIMEN_NAMER_STATE_DIR_PATH/"state"

logger.info("SYSTEM_SETTINGS_DIR_PATH=%s",str(SYSTEM_SETTINGS_DIR_PATH))
logger.info("USER_SETTINGS_DIR_PATH=%s",str(USER_SETTINGS_DIR_PATH))
logger.info("USER_LOGFILE=%s",str(USER_LOGFILE))
logger.info("SYSTEM_SETTINGS_FILE_PATH=%s",str(SYSTEM_SETTINGS_FILE_PATH))
logger.info("USER_SETTINGS_FILE_PATH=%s",str(USER_SETTINGS_FILE_PATH))
logger.info("PROTOCOL_CONFIG_DIR_PATH=%s",str(PROTOCOL_CONFIG_DIR_PATH))
logger.info("SPECIMEN_NAMES_TEMPLATE_DIR_PATH=%s",str(SPECIMEN_NAMES_TEMPLATE_DIR_PATH))
logger.info("SPECIMEN_NAMER_STATE_FILE_PATH=%s",str(SPECIMEN_NAMER_STATE_FILE_PATH))

# ensure that settings directories and files exist, if not create them by 
# copying from the default settings shipped with the codebase
__cur_dir = Path(__file__).parent.resolve()
__DEFAULT_SYSTEM_SETINGS_DIR=__cur_dir / "data/settings/site"
assert __DEFAULT_SYSTEM_SETINGS_DIR.is_dir(), f"could not find {__DEFAULT_SYSTEM_SETINGS_DIR}"

__DEFAULT_USER_SETINGS_DIR=__cur_dir / "data/settings/user"
assert __DEFAULT_USER_SETINGS_DIR.is_dir(), f"could not find {__DEFAULT_USER_SETINGS_DIR}"

if not USER_LOGFILE.parent.is_dir():
    logger.info("could not find user log dir, now creating %s",USER_LOGFILE.parent)
    USER_LOGFILE.parent.mkdir()

if not SPECIMEN_NAMER_STATE_DIR_PATH.is_dir():
    logger.info("could not find specimen name state dir, now creating %s",SPECIMEN_NAMER_STATE_DIR_PATH)    
    SPECIMEN_NAMER_STATE_DIR_PATH.mkdir()

if not SPECIMEN_NAMES_TEMPLATE_DIR_PATH.is_dir():
    logger.info("could not find specimen name template dir, now creating %s",SPECIMEN_NAMES_TEMPLATE_DIR_PATH)
    SPECIMEN_NAMES_TEMPLATE_DIR_PATH.mkdir()

if not SYSTEM_SETTINGS_DIR_PATH.is_dir():
    logger.info("could not find system settings, now creating %s", SYSTEM_SETTINGS_DIR_PATH)
    shutil.copytree(__DEFAULT_SYSTEM_SETINGS_DIR,SYSTEM_SETTINGS_DIR_PATH)

if not USER_SETTINGS_DIR_PATH.is_dir():
    logger.info("could not find user settings, now creating %s", USER_SETTINGS_DIR_PATH)
    shutil.copytree(__DEFAULT_USER_SETINGS_DIR,USER_SETTINGS_DIR_PATH)
