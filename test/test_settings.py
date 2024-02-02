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
from pywinauto import application,findwindows, mouse, Desktop, keyboard
from pywinauto.keyboard import send_keys
import pywinauto.timings
import pyautogui
import click

#local imports
from experiment_info import get_experiment_info, ExperimentInfo
from protocol import Protocol_HBE_A,Protocol_HBE_B
from application import TRIOS,DataLogger

logger = logging.getLogger(__name__)

if __name__ == "__main__":
    
    trios = TRIOS.connect()
  
    trios.set_settings({'velocity':100})
    