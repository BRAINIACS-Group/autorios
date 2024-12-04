#STL imports
from pathlib import Path

#3rd party imports
import platformdirs



SYSTEM_SETTINGS_FILE_PATH = Path(platformdirs.site_config_dir()) / "autotrios" / "settings.yaml"
USER_SETTINGS_DIR_PATH = Path(platformdirs.user_config_dir()) / "autotrios"