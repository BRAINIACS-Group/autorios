'''@Jan: This should contain a general description what this file does'''

# This script was written in  a sequential format considering the behaviour of the UI
# Any deviations will result in errors

#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any
import time
import sys
import re
import logging
from dataclasses import dataclass
from pathlib import Path
import tempfile
from abc import ABC
from collections import namedtuple
from enum import Enum

logging.basicConfig(level=logging.DEBUG)

#3rd party modules
from collections import namedtuple
import pywinauto
#local imports
from protocol import Protocol_HBE_A,Protocol_HBE_B
from application import DataLogger

logger = logging.getLogger(__name__)

def is_button(ctrl)->bool:
    return ctrl.element_info.class_name == "Button"

if __name__ == "__main__":
    
    dl = DataLogger.start()
    dl.set_path(Path(r"C:\Users\iwtm663\Documents\trios_automation\test\out\datalogger\test.txt"))
    #dl.connect_rheometer()
    #time.sleep(5)
    dl.start_recording()

    time.sleep(5)
    dl.stop_recording()
    dl.exit()