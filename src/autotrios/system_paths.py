#STL imports
from pathlib import Path
import logging
import shutil

#3rd party imports
import platformdirs

logger = logging.getLogger(__name__)

SYSTEM_SETTINGS_DIR_PATH = Path(platformdirs.site_config_dir()) / "autotrios"
USER_SETTINGS_DIR_PATH = Path(platformdirs.user_config_dir()) / "autotrios"

SYSTEM_SETTINGS_FILE_PATH = SYSTEM_SETTINGS_DIR_PATH / "settings.yaml"
USER_SETTINGS_FILE_PATH   = USER_SETTINGS_DIR_PATH / "settings.yaml"

PROTOCOL_CONFIG_DIR_PATH = USER_SETTINGS_DIR_PATH / "protocols"

# ensure that settings directories and files exist, if not create them by 
# copying from the default settings shipped with the codebase
__cur_dir = Path(__file__).parent.resolve()
__DEFAULT_SYSTEM_SETINGS_DIR=__cur_dir / "data/settings/site"
assert __DEFAULT_SYSTEM_SETINGS_DIR.is_dir(), f"could not find {__DEFAULT_SYSTEM_SETINGS_DIR}"

__DEFAULT_USER_SETINGS_DIR=__cur_dir / "data/settings/user"
assert __DEFAULT_USER_SETINGS_DIR.is_dir(), f"could not find {__DEFAULT_USER_SETINGS_DIR}"

if not SYSTEM_SETTINGS_DIR_PATH.is_dir():
    logger.info("could not find system settings, now creating %s", SYSTEM_SETTINGS_DIR_PATH)
    shutil.copytree(__DEFAULT_SYSTEM_SETINGS_DIR,SYSTEM_SETTINGS_DIR_PATH)

if not USER_SETTINGS_DIR_PATH.is_dir():
    logger.info("could not find user settings, now creating %s", USER_SETTINGS_DIR_PATH)
    shutil.copytree(__DEFAULT_USER_SETINGS_DIR,USER_SETTINGS_DIR_PATH)
