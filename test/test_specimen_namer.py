import unittest
import logging

from PySide6.QtWidgets import QApplication

from autotrios.specimen_namer import get_name_from_dialog
from autotrios.system_paths import USER_SPECIMEN_NAMES_TEMPLATE_DIR_PATH,SYSTEM_SPECIMEN_NAMES_TEMPLATE_DIR_PATH,SPECIMEN_NAMER_STATE_FILE_PATH

logging.basicConfig(level=logging.DEBUG)

class TestSpecimenNamer(unittest.TestCase):

    def test_get_name(self):
        app = QApplication()
        get_name_from_dialog(
            [USER_SPECIMEN_NAMES_TEMPLATE_DIR_PATH,SYSTEM_SPECIMEN_NAMES_TEMPLATE_DIR_PATH],
            statefile=SPECIMEN_NAMER_STATE_FILE_PATH
        )