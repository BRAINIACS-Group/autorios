import sys
from pathlib import Path
import time
import logging

from PyQt5.QtWidgets   import  QApplication

from autotrios.block_user_input import block_user_input



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication(sys.argv)
    with block_user_input(10):#
        time.sleep(5)