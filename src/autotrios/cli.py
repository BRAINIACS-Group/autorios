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
from tkinter import filedialog

import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2
#3rd party modules
from pywinauto import application, mouse
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
import pywinauto.timings
import pyautogui
import click

#local imports
#from .experiment_info import get_experiment_info, ExperimentInfo
from pyqtgui import get_experiment_info, ExperimentInfo
#from protocol import Protocol_HBE_A,Protocol_HBE_B
from protocol1 import Protocol
#from .protocol import Protocol_HBE_A_red,Protocol_HBE_B_red
from application1 import TRIOS

#@jan: try to follow the google python style guide:
#https://google.github.io/styleguide/pyguide.html
#pylint helps to automatically ensure this
#Formating: try to keep the line width to 80columns, use  \ for multiline
#continuation
#Fail fast and informative -->Use exceptions where an error might occur
#use r before strings to prevent escaping characters

logger = logging.getLogger(__name__)

@click.command()
@click.option('--start/--no-start',default=False)
@click.option('--debug/--no-debug',default=False)
def cli(start:bool,debug:bool):
    if debug:
        experiment_info = ExperimentInfo(
            sample_name='test',
            operator_name='tester',
            save_path_trios=Path(r'C:\Users\iwtm663\Documents\trios_automation\test\out\trios'),
            save_path_datalogger=Path(r'C:\Users\iwtm663\Documents\trios_automation\test\out\datalogger'),
            )
    
    else:
        experiment_info = get_experiment_info()

    '''protocols = [
        Protocol_HBE_A(),
        Protocol_HBE_B(),
    ]'''
    experiment_status = experiment_info.exp_status
    while experiment_status:
        logger.info("starting the exepriment")
        data_from_protocol = Protocol(experiment_info)
        protocols = list(data_from_protocol.p_data.keys())
        trios_app = TRIOS.connect(start_if_not_open=start)
        trios_app.run(experiment_info,protocols,data_from_protocol)
        experiment_info = get_experiment_info()
        experiment_status = experiment_info.exp_status
