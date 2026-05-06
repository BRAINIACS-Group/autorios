import unittest

from PySide6.QtWidgets import QApplication

from autotrios.specimen_namer import NamingDialog

class TestSpecimenNamer(unittest.TestCase):

    def test_get_name(self):
        app = QApplication()
        NamingDialog.get_name(patterns_folder=)
