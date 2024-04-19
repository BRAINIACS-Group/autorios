'''@Jan: This should contain a general description what this file does'''

# This script was written in  a sequential format considering the behaviour of the UI
# Any deviations will result in errors

#@Jan: sorting imports can help with an overview
#STL modules
from __future__ import annotations
from typing import List,NamedTuple,Dict,Any
import sys
import logging
from pathlib import Path

import sys
import warnings
warnings.simplefilter("ignore", UserWarning)
sys.coinit_flags = 2

#3rd party modules
import click

#local imports
#from .experiment_info import get_experiment_info, ExperimentInfo
from .pyqtgui import get_experiment_info, ExperimentInfo
#from protocol import Protocol_HBE_A,Protocol_HBE_B
from .protocol import Protocol
#from .protocol import Protocol_HBE_A_red,Protocol_HBE_B_red
from .application import TRIOS
from .settings import GlobalSettings

#@jan: try to follow the google python style guide:
#https://google.github.io/styleguide/pyguide.html
#pylint helps to automatically ensure this
#Formating: try to keep the line width to 80columns, use  \ for multiline
#continuation
#Fail fast and informative -->Use exceptions where an error might occur
#use r before strings to prevent escaping characters

logger = logging.getLogger(__name__)

SETTINGS_FILE_PATH = Path(__file__).resolve().parents[2] / 'settings' / 'settings.yaml'

@click.command()
@click.option('--start/--no-start',default=False)
@click.option('--debug/--no-debug',default=False)
@click.option('--settings_file',default='')
def cli(start:bool,debug:bool,settings_file_path:str):
    '''comand line interface entry point
    Args:
    start: 
    '''
    
    if not settings_file_path:
        settings_file_path = SETTINGS_FILE_PATH
    global_settings = GlobalSettings.from_file(settings_file_path)

    while True:
        if debug:
            experiment_info = ExperimentInfo(
                sample_name='test',
                operator_name='tester',
                save_path_trios=Path(r'C:\Users\iwtm663\Documents\trios_automation\test\out\trios'),
                save_path_datalogger=Path(r'C:\Users\iwtm663\Documents\trios_automation\test\out\datalogger'),
                )
        
        else:
            experiment_info = get_experiment_info(global_settings.protocol_config_path)

        experiment_status = experiment_info.exp_status
    
        logger.info("starting the exepriment")        
        data_from_protocol = Protocol(experiment_info)
        #protocols = list(data_from_protocol.p_data.keys())
        
        trios_app = TRIOS.connect(start_if_not_open=start,
            datalogger_restart=global_settings.datalogger_restart)
        trios_app.run(experiment_info)
        
        if debug:
            break

        experiment_info = get_experiment_info()        
