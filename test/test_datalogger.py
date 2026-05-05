
#STL imports
import unittest
from pathlib import Path
import tempfile
import time
import logging

#autotrios improts
from autotrios.datalogger import DataLogger

logger = logging.getLogger(__name__)

datalogger_windowname="ARG2AuxiliarySample"
datalogger_paths=[
    Path(r"C:\Program Files (x86)\TA Instruments\TRIOS\ARG2AuxiliarySample.exe"),
    Path(r"C:\Program Files\TA Instruments\TRIOS\ARG2AuxiliarySample.exe"),
    ]

class TestDatalogger(unittest.TestCase):

    def test_start(self):
        dl = DataLogger.start(datalogger_windowname,datalogger_paths)
        dl.exit()

    def test_connect(self):
        dl = DataLogger.start(datalogger_windowname,datalogger_paths)
        dl.connect_rheometer()
        dl.exit()

    def test_set_path(self):
        dl = DataLogger.start(datalogger_windowname,datalogger_paths)
        with tempfile.TemporaryDirectory() as td:
            tf = Path(td) / "testfile.txt"
            dl.set_path(tf)
            tf.touch()
            with self.assertRaises(FileExistsError):
                dl.set_path(tf)
            dl.exit()

    def test_recording(self):
        dl = DataLogger.start(datalogger_windowname,datalogger_paths)
        with tempfile.TemporaryDirectory(delete=False) as td:
            tf = Path(td) / r"testfääöö..§~  $%"
            dl.set_path(Path(tf))
            dl.connect_rheometer()
            dl.start_recording()
            time.sleep(1)
            dl.stop_recording()
            time.sleep(1)
            try:
                tf_txt = tf.with_name(tf.name + ".txt")
                self.assertTrue(tf_txt.is_file())
            except Exception:
                logger.error(f"exception, file not found: {tf_txt}")
                raise
            finally:
                dl.exit()
            time.sleep(1)
