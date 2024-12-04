#STL imports
from pathlib import Path
import logging
import shutil

#3rd party imports
import platformdirs

logger = logging.getLogger(__name__)

SYSTEM_SETTINGS_DIR_PATH = Path(platformdirs.site_config_dir()) / "autotrios"
SYSTEM_SETTINGS_FILE_PATH = SYSTEM_SETTINGS_DIR_PATH / "settings.yaml"

USER_SETTINGS_DIR_PATH = Path(platformdirs.user_config_dir()) / "autotrios"

__cur_dir = Path(__file__).parent.resolve()
__DEFAULT_SYSTEM_SETINGS_DIR=__cur_dir / "data/settings/site"
assert __DEFAULT_SYSTEM_SETINGS_DIR.is_dir(), f"could not find {__DEFAULT_SYSTEM_SETINGS_DIR}"

__DEFAULT_USER_SETINGS_DIR=__cur_dir / "data/settings/user"
assert __DEFAULT_USER_SETINGS_DIR.is_dir(), f"could not find {__DEFAULT_SYSTEM_SETINGS_DIR}"

if not SYSTEM_SETTINGS_DIR_PATH.is_dir():
    logger.info(f"could not find system settings, now creating {SYSTEM_SETTINGS_DIR_PATH}")
    shutil.copytree(__DEFAULT_SYSTEM_SETINGS_DIR,SYSTEM_SETTINGS_DIR_PATH)

if not USER_SETTINGS_DIR_PATH.is_dir():
    logger.info(f"could not find system settings, now creating {USER_SETTINGS_DIR_PATH}")
    shutil.copytree(__DEFAULT_USER_SETINGS_DIR,USER_SETTINGS_DIR_PATH)
