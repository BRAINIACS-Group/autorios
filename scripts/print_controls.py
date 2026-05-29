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
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

#3rd party modules
from pywinauto import application,findwindows, mouse, Desktop, keyboard
from pywinauto.keyboard import send_keys
import pywinauto.timings
import pyautogui
import click

#local imports
#from experiment_info import get_experiment_info, ExperimentInfo
#from protocol import Protocol_HBE_A,Protocol_HBE_B
#from application import TRIOS,DataLogger
from autorios.trios import TRIOS
from autorios.settings import get_settings_default

logger = logging.getLogger(__name__)

BACKEND="win32"
if __name__ == "__main__":
    trios_windowname="TA Instruments Trios"
    trios_paths=[
         Path(r"C:\Program Files (x86)\TA Instruments\TRIOS\Trios.exe"),
         Path(r"C:\Program Files\TA Instruments\TRIOS\Trios.exe"),
      ]
    app=None
    for path in trios_paths:
        try:
            app = application.Application(backend=BACKEND).connect(
                path=str(path),timeout=1)
            break
        except Exception as e:
            pass
    window_main = app.window(title_re=f".*{trios_windowname}.*")
    window_main.exists(2)
    window_main.dump_tree(filename='tree_trios_win32.txt')

    # tree_view = trios.window_main.child_window(title="treeViewAdv1")
    # tree_view.draw_outline("blue")
    # file_manager = trios.window_main.child_window(title="File Manager", control_type="Pane")
    # file_manager.print_control_identifiers(filename='file_manager.txt')
    # file_manager.draw_outline("red")
    # for child in file_manager.children()[0].children():
    #     time.sleep(.5)
    #     child.draw_outline()
    #     print(child)

    #for w in trios.app.windows(): #dump_tree(filename='tree_trios.txt')
    #    print(w)
    #for w in Desktop(backend="win32").windows():
    # #    print(w)
    # #print(Desktop(backend='win32')["Open procedure file"].exists())

    # trios.window_main.child_window(title_re="Gap.*").print_control_identifiers()

    # settings_window = trios.window_main.child_window(title="TA Instruments TRIOS", auto_id="MasterOptionsDialog", control_type="Window")
    # settings_window.wait('exists',1)
    # #time.sleep(2)
    # settings_window.print_control_identifiers(filename="tree_settings.txt")

    #dl = DataLogger.connect()
    #type_keys("test.txt")
    #dl.window_main.dump_tree(filename='tree_datalogger.txt')

    pass