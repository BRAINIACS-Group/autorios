import unittest
import logging

from PySide6.QtWidgets import QApplication

from autotrios.specimen_namer import NamingDialog
from autotrios.system_paths import SPECIMEN_NAMES_TEMPLATE_DIR_PATH

logging.basicConfig(level=logging.DEBUG)

class TestSpecimenNamer(unittest.TestCase):

    def test_get_name(self):
        app = QApplication()
        NamingDialog.get_name(patterns_folder=SPECIMEN_NAMES_TEMPLATE_DIR_PATH)
