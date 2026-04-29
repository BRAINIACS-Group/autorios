import sys
from pathlib import Path
import time
import threading
import logging

from PySide6.QtWidgets   import  QApplication

from autotrios.block_user_input import InputBlocker

logger = logging.getLogger()

def blockingfn(blocker:InputBlocker):
    with blocker:
        logger.info("blocking function")
        time.sleep(5)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    app = QApplication()
    countdown_blocker = InputBlocker(10,True)
    countdown_blocker.show()
    thread = threading.Thread(target=blockingfn,args=(countdown_blocker,))
    thread.daemon=True
    thread.start()
    logger.debug("running exec")
    app.exec()