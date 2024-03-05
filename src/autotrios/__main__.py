

#STL imports
import logging

#3rd party imports
from PyQt5.QtWidgets import QApplication

#local imports
from cli import cli

logging.basicConfig(level=logging.DEBUG)
app = QApplication([])
cli()
app.exec_()