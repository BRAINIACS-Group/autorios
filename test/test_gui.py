import sys
from pathlib import Path

from PyQt5.QtWidgets   import  QApplication

from autotrios.pyqtgui import AutoTriosGui



if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = AutoTriosGui(protocol_config_dir=Path("./protocols"))
    gui.show()
    sys.exit(app.exec_())